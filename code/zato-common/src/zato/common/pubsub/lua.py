# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

lua_publish = """

   local id_key = KEYS[1]
   local msg_values = KEYS[2]
   local msg_metadata_key = KEYS[3]
   local msg_expire_at = KEYS[4]
   local last_pub_time_key = KEYS[5]
   local last_seen_producer_key = KEYS[6]

   local score = ARGV[1]
   local msg_id = ARGV[2]
   local expire_at = ARGV[3]
   local msg_value = ARGV[4]
   local msg_metadata = ARGV[5]
   local topic_name = ARGV[6]
   local utc_now = ARGV[7]
   local client_id = ARGV[8]

   redis.pcall('zadd', id_key, score, msg_id)
   redis.pcall('hset', msg_values, msg_id, msg_value)
   redis.pcall('hset', msg_metadata_key, msg_id, msg_metadata)
   redis.pcall('hset', msg_expire_at, msg_id, expire_at)
   redis.pcall('hset', last_pub_time_key, topic_name, utc_now)
   redis.pcall('hset', last_seen_producer_key, client_id, utc_now)
"""

lua_move_to_target_queues = """

    -- A function to copy Redis keys we operate over to a table which skips the first one, the source queue.
    local function get_target_queues(keys, argv)
        local target_queues = {}
        local max_depths = {}
        if #keys == 4 then
          target_queues = {keys[4]}
          max_depths = {argv[4]}
        else
            for idx = 1, #keys do
                -- Note - the whole point is that we're skipping the first few items which are not target queues
                target_queues[idx] = keys[idx+3]
                max_depths[idx] = argv[idx+3]
            end
        end
        return {target_queues, max_depths}
    end

    local source_queue = KEYS[1]
    local backlog_full = KEYS[2]
    local unack_counter = KEYS[3]

    local is_fifo = tonumber(ARGV[1])
    local max_depth = tonumber(ARGV[2])
    local max_int = tonumber(ARGV[3])
    local zset_command
    local out = {}
    local target_queue_depth = 0
    local can_push_to_target = true;

    if is_fifo then
        zset_command = 'zrevrange'
    else
        zset_command = 'zrange'
    end

    local ids = redis.pcall(zset_command, source_queue, 0, max_depth)

    local target_queues_max_depths = get_target_queues(KEYS, ARGV)
    local target_queues = target_queues_max_depths[1]
    local max_depths = target_queues_max_depths[2]

    for queue_idx, target_queue in ipairs(target_queues) do

        for id_idx, id in ipairs(ids) do

            target_queue_depth = redis.call('llen', target_queue);

            max_depth = tonumber(max_depths[queue_idx])
            if target_queue_depth >= max_depth then
                can_push_to_target = false
            else
                can_push_to_target = true
            end

            if can_push_to_target then
                redis.call('lpush', target_queue, id)
                redis.pcall('hincrby', unack_counter, id, 1)
                table.insert(out, {'moved', target_queue, id})
            else
                table.insert(out, {'overflow', target_queue, id})
            end

            redis.pcall('zrem', source_queue, id)

        end
    end

    return out
    """

lua_get_from_cons_queue = """

   local cons_queue = KEYS[1]
   local cons_in_flight_ids = KEYS[2]
   local cons_in_flight_data = KEYS[3]
   local last_seen_consumer_key = KEYS[4]
   local msg_metadata_key = KEYS[5]
   local msg_key = KEYS[6]

   local max_batch_size = tonumber(ARGV[1])
   local utc_now = ARGV[2]
   local client_id = ARGV[3]

   local ids = redis.pcall('lrange', cons_queue, 0, max_batch_size)
   local values = {}

   redis.pcall('hset', last_seen_consumer_key, client_id, utc_now)

    -- It may well be the case that there are no messages for this client
    if #ids > 0 then

       for id_idx, id in ipairs(ids) do

           local msg = redis.pcall('hmget', msg_key, id)
           local metadata = redis.pcall('hmget', msg_metadata_key, id)
           table.insert(values, {msg, metadata})

           redis.pcall('sadd', cons_in_flight_ids, id)
           redis.pcall('hset', cons_in_flight_data, id, utc_now)
           redis.pcall('lrem', cons_queue, 0, id)
       end
    end

    return values

"""

lua_reject = """

   local cons_queue = KEYS[1]
   local cons_in_flight_ids = KEYS[2]
   local cons_in_flight_data = KEYS[3]
   local ids = ARGV
   local out = {}

   redis.pcall('hdel', cons_in_flight_data, unpack(ids))

    for id_idx, id in ipairs(ids) do
        if redis.pcall('srem', cons_in_flight_ids, id) == 1 then
            table.insert(out, id)
        end
        redis.pcall('lpush', cons_queue, id)
    end

    return out
"""

lua_ack_delete = """

    -- A function to copy IDs to a separate table out of ARGV
    local function get_ids(argv)
        local ids = {}
        for idx = 1, #argv do
            ids[idx] = argv[idx+1]
        end
        return ids
    end

    local cons_in_flight_ids = KEYS[1]
    local cons_in_flight_data = KEYS[2]
    local unack_counter = KEYS[3]
    local msg_values = KEYS[4]
    local msg_expire_at = KEYS[5]
    local msg_metadata_key = KEYS[6]
    local cons_queue = KEYS[7]
 
    local is_delete = ARGV[1]
    local ids = get_ids(ARGV)
    local unack_id_count = 0
    local out = {}

    for id_idx, id in ipairs(ids) do

        -- We're deleting a message from a consumer's queue, not merely ack'ing it.
        if is_delete == '1' then
            redis.pcall('lrem', cons_queue, 0, id)
        end

        if redis.pcall('srem', cons_in_flight_ids, id) == 1 then
            table.insert(out, id)
        end
        redis.pcall('hdel', cons_in_flight_data, id)
        unack_id_count = redis.pcall('hincrby', unack_counter, id, -1)

        -- It was the last confirmation we were waiting for so let's delete all traces of the message.

        if unack_id_count == 0 then
            redis.pcall('hdel', unack_counter, id)
            redis.pcall('hdel', msg_values, id)
            redis.pcall('hdel', msg_metadata_key, id)
            redis.pcall('hdel', msg_expire_at, id)
        end

    end

    return out

"""

lua_delete_expired_topic = """

    local id_key = KEYS[1]
    local msg_values = KEYS[2]
    local msg_metadata_key = KEYS[3]
    local msg_expire_at = KEYS[4]

    local now_utc = tostring(ARGV[1])
    local expired = {}

    local ids = redis.pcall('zrange', id_key, 0, 500)

    for id_idx, id in ipairs(ids) do

        -- Expiration times can be compared lexicographically because we use ISO-8601, i.e. 2014-02-16T02:51:24.013459
        local expire_at = tostring(redis.pcall('hget', msg_expire_at, id))

        if now_utc > expire_at then
            redis.pcall('zrem', id_key, id)
            redis.pcall('hdel', msg_values, id)
            redis.pcall('hdel', msg_metadata_key, id)
            redis.pcall('hdel', msg_expire_at, id)
            table.insert(expired, id)
        end
    end

    return expired

"""

lua_delete_expired_consumer = """
    local consumer_msg_ids = KEYS[1]
    local cons_in_flight_ids = KEYS[2]
    local msg_values = KEYS[3]
    local msg_expire_at = KEYS[4]
    local unack_counter = KEYS[5]

    local now_utc = tostring(ARGV[1])
    local expired = {}

    -- Grab a batch of IDs to check their expiration
    local ids = redis.pcall('lrange', consumer_msg_ids, 0, 500)

    for id_idx, id in ipairs(ids) do

        -- The message may be expired but the result other than 0 means it's still in flight - we don't do anything with these.
        -- It's possible they can block the whole consumer queue but in that case a user intervention will be needed.

        if redis.pcall('sismember', id, cons_in_flight_ids) == 0 then

            -- Ok, we know the message is not in-flight so grab the time it expires at and compare it with now.
            -- Note that we're using ISO-8601 dates in the format of 2014-02-16T02:51:24.013459 so we can always
            -- compare expiration times lexicographically.

            local expire_at = tostring(redis.pcall('hget', msg_expire_at, id))

            -- The message has indeed expired so we can safely delete every piece of information on it.
            if now_utc > expire_at then
                redis.pcall('lrem', consumer_msg_ids, 0, id)
                redis.pcall('hdel', msg_values, id)
                redis.pcall('hdel', msg_expire_at, id)
                redis.pcall('hdel', unack_counter, id)
                table.insert(expired, id)
            end
        end
    end

    return expired

"""

lua_get_message_list = """
    local source_ids_key = KEYS[1]
    local metadata_key = KEYS[2]

    local source_type = ARGV[1]
    local data = {}
    local redis_call = ''

    if source_type == 'topic' then
       redis_call = 'zrange'
    else
       redis_call = 'lrange'
    end

    local ids = redis.pcall(redis_call, source_ids_key, 0, -1)

    for id_idx, id in ipairs(ids) do
       table.insert(data, redis.pcall('hget', metadata_key, id))
    end

    return data
"""

lua_delete_from_topic = """
   local ids_key = KEYS[1]
   local msg_values = KEYS[2]
   local msg_metadata_key = KEYS[3]
   local msg_expire_at = KEYS[4]

   local has_consumers = ARGV[1]
   local msg_id = ARGV[2]

   local result = {has_consumers}

   if has_consumers == '0' then
       table.insert(result, 'has_consumers_false')
       table.insert(result, redis.pcall('zrem', ids_key, msg_id))
       table.insert(result, redis.pcall('hdel', msg_values, msg_id))
       table.insert(result, redis.pcall('hdel', msg_metadata_key, msg_id))
       table.insert(result, redis.pcall('hdel', msg_expire_at, msg_id))
   else
       table.insert(result, 'has_consumers_true')
       table.insert(result, redis.pcall('zrem', ids_key, msg_id))
   end

   return result

"""
