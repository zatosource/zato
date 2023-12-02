
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.redis.CommandInfo = new Class({
    toString: function() {
        var s = '<CommandInfo name:[{0}], template:[{1}], desc:[{2}]>';
        return String.format(s, this.name ? this.name : '(none)',
                                this.template ? this.template : '(none)',
                                this.desc ? this.desc : '(none)'
        );
    }
});

// /////////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.redis.command_info = new Object();
    var ci_list = [
        ['CONFIG GET', 'CONFIG GET parameter', 'Get the value of a configuration parameter'],
        ['CONFIG SET', 'CONFIG SET parameter value', 'Set a configuration parameter to the given value'],
        ['CONFIG RESETSTAT', 'CONFIG RESETSTAT', 'Reset the stats returned by INFO'],
        ['DBSIZE', 'DBSIZE', 'Return the number of keys in the selected database'],
        ['DECR', 'DECR key', 'Decrement the integer value of a key by one'],
        ['DECRBY', 'DECRBY key decrement', 'Decrement the integer value of a key by the given number'],
        ['DEL', 'DEL key [key ...]', 'Delete a key'],
        ['DUMP', 'DUMP key', 'Return a serialized verison of the value stored at the specified key'],
        ['ECHO', 'ECHO message', 'Echo the given string'],
        ['EXISTS', 'EXISTS key', 'Determine if a key exists'],
        ['EXPIRE', 'EXPIRE key seconds', 'Set a key\'s time to live in seconds'],
        ['EXPIREAT', 'EXPIREAT key timestamp', 'Set the expiration for a key as a UNIX timestamp'],
        ['FLUSHDB', 'FLUSHDB', 'Remove all keys from the current database'],
        ['GET', 'GET key', 'Get the value of a key'],
        ['HDEL', 'HDEL key field [field ...]', 'Delete one or more hash fields'],
        ['HEXISTS', 'HEXISTS key field', 'Determine if a hash field exists'],
        ['HGET', 'HGET key field', 'Get the value of a hash field'],
        ['HGETALL', 'HGETALL key', 'Get all the fields and values in a hash'],
        ['HINCRBY', 'HINCRBY key field increment', 'Increment the integer value of a hash field by the given number'],
        ['HKEYS', 'HKEYS key', 'Get all the fields in a hash'],
        ['HLEN', 'HLEN key', 'Get the number of fields in a hash'],
        ['HSET', 'HSET key field value', 'Set the string value of a hash field'],
        ['HSETNX', 'HSETNX key field value', 'Set the value of a hash field, only if the field does not exist'],
        ['HVALS', 'HVALS key', 'Get all the values in a hash'],
        ['INCR', 'INCR key', 'Increment the integer value of a key by one'],
        ['INCRBY', 'INCRBY key increment', 'Increment the integer value of a key by the given amount'],
        ['INFO', 'INFO', 'Get information and statistics about the server'],
        ['KEYS', 'KEYS pattern', 'Find all keys matching the given pattern'],
        ['LLEN', 'LLEN key', 'Get the length of a list'],
        ['LPOP', 'LPOP key', 'Remove and get the first element in a list'],
        ['LPUSH', 'LPUSH key value [value ...]', 'Prepend one or multiple values to a list'],
        ['LPUSHX', 'LPUSHX key value', 'Prepend a value to a list, only if the list exists'],
        ['LRANGE', 'LRANGE key start stop', 'Get a range of elements from a list'],
        ['LREM', 'LREM key count value', 'Remove elements from a list'],
        ['LSET', 'LSET key index value', 'Set the value of an element in a list by its index'],
        ['LTRIM', 'LTRIM key start stop', 'Trim a list to the specified range'],
        ['MGET', 'MGET key [key ...]', 'Get the values of all the given keys'],
        ['MSET', 'MSET key value [key value ...]', 'Set multiple keys to multiple values'],
        ['MSETNX', 'MSETNX key value [key value ...]', 'Set multiple keys to multiple values, only if none of the keys exist'],
        ['OBJECT', 'OBJECT subcommand [arguments [arguments ...]]', 'Inspect the internals of Redis objects'],
        ['PERSIST', 'PERSIST key', 'Remove the expiration from a key'],
        ['PEXPIRE', 'PEXPIRE key milliseconds', 'Set a key\'s time to live in milliseconds'],
        ['PEXPIREAT', 'PEXPIREAT key milliseconds-timestamp', 'Set the expiration for a key as a UNIX timestamp specified in milliseconds'],
        ['PING', 'PING', 'Ping the server'],
        ['PSETEX', 'PSETEX key milliseconds value', 'Set the value and expiration in milliseconds of a key'],
        ['PTTL', 'PTTL key', 'Get the time to live for a key in milliseconds'],
        ['RANDOMKEY', 'RANDOMKEY', 'Return a random key from the keyspace'],
        ['RENAME', 'RENAME key newkey', 'Rename a key'],
        ['RENAMENX', 'RENAMENX key newkey', 'Rename a key, only if the new key does not exist'],
        ['RESTORE', 'RESTORE key ttl serialized-value', 'Create a key using the provided serialized value, previously obtained using DUMP'],
        ['RPOP', 'RPOP key', 'Remove and get the last element in a list'],
        ['SADD', 'SADD key member [member ...]', 'Add one or more members to a set'],
        ['SET', 'SET key value', 'Set the string value of a key'],
        ['SISMEMBER', ' SISMEMBER key member', 'Returns if member is a member of the set stored at key'],
        ['SMEMBERS', 'SMEMBERS key', 'Get all the members in a set'],
        ['SREM', 'SREM key member [member ...]', 'Remove one or more members from a set'],
        ['TIME', 'TIME', 'Return the current server time'],
        ['TTL', 'TTL key', 'Get the time to live for a key'],
        ['TYPE', 'TYPE key', 'Determine the type stored at key'],
        ['ZADD', 'ZADD key score member [score] [member]', 'Add one or more members to a sorted set, or update its score if it already exists'],
        ['ZRANGE', 'ZRANGE key start stop [WITHSCORES]', 'Return a range of members in a sorted set, by index'],
        ['ZREM', 'ZREM key member [member ...]', 'Remove one or more members from a sorted set'],
    ];

    _.each(ci_list, function(elem) {
        var ci = new $.fn.zato.outgoing.redis.CommandInfo();
        ci.name = elem[0];
        ci.template = elem[1];
        ci.desc = elem[2];
        $.fn.zato.outgoing.redis.command_info[ci.name] = ci;
    });

// /////////////////////////////////////////////////////////////////////////////


$(document).ready(function() {

    var command_form = $('#command-form');

    var _callback = function(data, status, xhr){
        var success = status == 'success';
        $("#id_result").text('');

        if(success) {
            var div = $('#user-message-div');
            div.fadeOut(100);
            $("#id_result").text(data.message);
        }
        else {
            $.fn.zato.user_message(false, data.responseText);
        }
    }

    var options = {
        success: _callback,
        error:  _callback,
        resetForm: false,
        dataType: 'json',
    };

    command_form.submit(function() {
        $(this).ajaxSubmit(options);
        return false;
    });

});


$.fn.zato.outgoing.redis.command_help = function(command) {
    var ci = $.fn.zato.outgoing.redis.command_info[command];
    $('#command-help').html('<span style="text-shadow:1px 1px 0px #eee">' + ci.template + '<br/>' + '<span style="color:#444">' + ci.desc + '</span>' + '</span>');
}

$.fn.zato.outgoing.redis.command_template = function(command) {
    var ci = $.fn.zato.outgoing.redis.command_info[command];
    $('#id_command').val(ci.template);
}
