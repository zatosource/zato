/**
 * String.format for JavaScript 1.09
 * mstr.se/sffjs
 *  
 * Built: 2014-01-26T13:12:33Z
 *
 * Copyright (c) 2009-2014 Daniel Mester Pirttijärvi
 *
 * This software is provided 'as-is', without any express or implied
 * warranty.  In no event will the authors be held liable for any damages
 * arising from the use of this software.
 * 
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 * 
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 * 
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 
 * 3. This notice may not be removed or altered from any source distribution.
 * 
 */

var sffjs = (function() {

    // ***** Public Interface *****
    var sffjs = {
            /// <field name="version" type="String">The version of the library String.Format for JavaScript.</field>
            version: "1.09",
            
            setCulture: function (languageCode) {
                /// <summary>
                ///     Sets the current culture, used for culture specific formatting.
                /// </summary>
                /// <param name="LCID">The IETF language code of the culture, e.g. en-US or en.</param>
                
                currentCultureId = languageCode;
                updateCulture();
            },
            
            registerCulture: function (culture) {
                /// <summary>
                ///     Registers an object containing information about a culture.
                /// </summary>
                
                cultures[culture.name[toUpperCase]()] = fillGapsInCulture(culture);
                
                // ...and reevaulate current culture
                updateCulture();
            }
        },
        
    // ***** Shortcuts *****
        _Number = Number,
        _String = String,
        zero = "0",
        toUpperCase = "toUpperCase",
        undefined,
   
    // ***** Private Variables *****
    
        // This is the default values of a culture. Any missing format will default to the format in CULTURE_TEMPLATE.
        // The invariant culture is generated from these default values.
        CULTURE_TEMPLATE = {
            name: "", // Empty on invariant culture
            d: "MM/dd/yyyy",
            D: "dddd, dd MMMM yyyy",
            t: "HH:mm",
            T: "HH:mm:ss",
            M: "MMMM dd",
            Y: "yyyy MMMM",
            s: "yyyy-MM-ddTHH:mm:ss",
            _M: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
            _D: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            _r: ".", // Radix point
            _t: ",", // Thounsands separator
            _c: "¤#,0.00", // Currency format string
            _ct: ",", // Currency thounsands separator
            _cr: ".",  // Currency radix point
            _am: "AM",
            _pm: "PM"
        },
    
        // Generate invariant culture
        INVARIANT_CULTURE = fillGapsInCulture({}),
    
        // Holds the current culture object
        currentCulture,
    
        // Holds the id of the current culture. The id is also included in the culture object, but the 
        // culture object might be replaced during runtime when a better matching culture is registered.
        currentCultureId = navigator.systemLanguage || navigator.language || "",
    
        // Holds all registered external cultures, i.e. not the invariant culture
        cultures = {};
    
    
    // ***** Private Methods *****
    
    // General helpers
    
    function numberPair(n) {
        /// <summary>Converts a number to a string that is at least 2 digit in length. A leading zero is inserted as padding if necessary.</summary>
        return n < 10 ? zero + n : n;
    }

    function hasValue(value) {
        /// <summary>Returns true if <paramref name="value"/> is not null or undefined.</summary>
        return value !== null && value !== undefined;
    }
    
    function numberCoalesce(value1, value2) {
        /// <summary>Returns the first of the two values that is not NaN.</summary>
        return isNaN(value1) ? value2 : value1;
    }
    
    
    // Culture functions
    
    function fillGapsInCulture(culture) {
        /// <summary>This method will fill gaps in the specified culture with information from the invariant culture.</summary>
        
        // Add missing formats from the culture template
        for (var key in CULTURE_TEMPLATE) {
            culture[key] = culture[key] || CULTURE_TEMPLATE[key];
        }
        
        // Construct composite formats if they are not already defined
        culture.f = culture.f || culture.D + " " + culture.t;
        culture.F = culture.F || culture.D + " " + culture.T;
        culture.g = culture.g || culture.d + " " + culture.t;
        culture.G = culture.G || culture.d + " " + culture.T;
        
        // Add aliases
        culture.m = culture.M;
        culture.y = culture.Y;
        
        return culture;
    }
    
    function updateCulture() {
        /// <summary>This method will update the currently selected culture object to reflect the currently set LCID (as far as possible).</summary>
        sffjs.LC = currentCulture = 
            currentCultureId && 
            (
                cultures[currentCultureId[toUpperCase]()] || 
                cultures[currentCultureId.split("-")[0][toUpperCase]()]
            ) || INVARIANT_CULTURE;
    }
    
    
    // Maths
    
    function numberToString(number, decimals) {
        /// <summary>Generates a string representation of the specified number with the specified number of digits.</summary>
        /// <param name="number" type="Number">The value to be processed.</param>
        /// <param name="decimals" type="Number" integer="true" optional="true">The maximum number of decimals. If not specified, the value is not rounded.</param>
        /// <returns>The rounded absolute value as a string.</returns>
        var roundingFactor = Math.pow(10, decimals || 0);
        return "" + (Math.round(Math.abs(number) * roundingFactor) / roundingFactor);
    }
    
    function numberOfIntegralDigits(numberString) {
        /// <summary>Counts the number of integral digits in a number converted to a string by the JavaScript runtime.</summary>
        var point = numberString.indexOf(".");
        return point < 0 ? numberString.length : point;
    }
    
    function numberOfDecimalDigits(numberString) {
        /// <summary>Counts the number of decimal digits in a number converted to a string by the JavaScript runtime</summary>
        var point = numberString.indexOf(".");
        return point < 0 ? 0 : numberString.length - point - 1;
    }
    
    
    // Formatting helpers
    
    function resolvePath(path, value) {
        /// <summary>
        ///     This function resolves a path on the format <membername>(.<membername>|[<index>])*
        ///     and evaluates the value.
        /// </summary>
        /// <param name="path">A series of path components separated by points. Each component is either an index in square brackets.</param>
        /// <param name="value">An object on which the path is evaluated.</param>
        
        // Parse and evaluate path
        if (hasValue(value)) {
            var followingMembers = /(\.([a-zA-Z_$]\w+)|\[(\d+)\])/g,
                match = /^[a-zA-Z_$]\w+/.exec(path);
                
            value = value[match[0]];
            
            // Evaluate path until we reach the searched member or the value is undefined/null
            while (hasValue(value) && (match = followingMembers.exec(path))) {
                value = value[match[2] || _Number(match[3])];
            }
        }
        
        return value;
    };
    
    function groupedAppend(out, value) {
        /// <summary>Writes a value to an array in groups of three digits.</summary>
        /// <param name="out" type="Array">
        ///     An array used as string builder to which the grouped output will be appended. The array 
        ///     may have to properties that affect the output:
        ///
        ///         g: the number of integral digits left to write.
        ///         t: the thousand separator.
        ///
        //      If any of those properties are missing, the output is not grouped.
        /// </param>
        /// <param name="value" type="String">The value that will be written to <paramref name="out"/>.</param>
        
        for (var i = 0, length = value.length; i < length; i++) {
            // Write number
            out.push(value.charAt(i));

            // Begin a new group?
            if (out.g > 1 && out.g-- % 3 == 1) {
                out.push(out.t);
            }
        }
    }
    
    function unescapeBraces(braces, consumedBraces) {
        /// <summary>Replaces escaped brackets ({ and }) with their unescaped representation.</summary>
        /// <param name="braces">A string containing braces of a single type only.</param>
        /// <param name="consumedBraces">The number of braces that should be ignored when unescaping.</param>
        /// <returns>A string of the unescaped braces.</returns>
        return braces.substr(0, (braces.length + 1 - (consumedBraces || 0)) / 2);
    }
    
    function processFormatItem(pathOrIndex, align, formatString, args) {        
        /// <summary>Process a single format item in a composite format string</summary>
        /// <param name="pathOrIndex" type="String">The raw argument index or path component of the format item.</param>
        /// <param name="align" type="String">The raw alignment component of the format item.</param>
        /// <param name="formatString" type="String">The raw format string of the format item.</param>
        /// <param name="args" type="Array">The arguments that were passed to String.format, where index 0 is the full composite format string.</param>
        /// <returns>The formatted value as a string.</returns>
        
        var value, 
            index = parseInt(pathOrIndex, 10), 
            paddingLength, 
            padding = "";
        
        // Determine whether index or path mode was used
        if (isNaN(index)) {
            // Non-numerical index => treat as path
            value = resolvePath(pathOrIndex, args[1]);
        } else {
            // Index was numerical => ensure index is within range
            if (index > args.length - 2) {
                // Throw exception if argument is not specified (however undefined and null values are fine!)
                throw "Missing argument";
            }
            
            value = args[index + 1];
        }
        
        // If the object has a custom format method, use it,
        // otherwise use toString to create a string
        value = !hasValue(value) ? "" : value.__Format ? value.__Format(formatString) : "" + value;
        
        // Add padding (if necessary)
        align = _Number(align) || 0;
        
        paddingLength = Math.abs(align) - value.length;

        while (paddingLength-- > 0) {
            padding += " ";
        }
        
        // innerArgs[1] is the leading {'s
        return (align < 0 ? value + padding : padding + value);
    }
    
    function basicNumberFormatter(number, minIntegralDigits, minDecimalDigits, maxDecimalDigits, radixPoint, thousandSeparator) {
        /// <summary>Handles basic formatting used for standard numeric format strings.</summary>
        /// <param name="number" type="Number">The number to format.</param>
        /// <param name="minIntegralDigits" type="Number" integer="true">The minimum number of integral digits. The number is padded with leading zeroes if necessary.</param>
        /// <param name="minDecimals" type="Number" integer="true">The minimum number of decimal digits. The decimal part is padded with trailing zeroes if necessary.</param>
        /// <param name="maxDecimals" type="Number" integer="true">The maximum number of decimal digits. The number is rounded if necessary.</param>
        /// <param name="radixPoint" type="String">The string that will be appended to the output as a radix point.</param>
        /// <param name="thousandSeparator" type="String">The string that will be used as a thousand separator of the integral digits.</param>
        /// <returns>The formatted value as a string.</returns>
        
        var integralDigits, decimalDigits, out = [];
        out.t = thousandSeparator;
        
        // Minus sign
        if (number < 0) {
            out.push("-");
        }
        
        // Prepare number 
        number = numberToString(number, maxDecimalDigits);
        
        integralDigits = out.g = numberOfIntegralDigits(number);
        decimalDigits = numberOfDecimalDigits(number);

        // Pad integrals with zeroes to reach the minimum number of integral digits
        minIntegralDigits -= integralDigits;
        while (minIntegralDigits-- > 0) {
            groupedAppend(out, zero);
        }
        
        // Add integral digits
        groupedAppend(out, number.substr(0, integralDigits));
        
        // Add decimal point and decimal digits
        if (minDecimalDigits || decimalDigits) {
            out.push(radixPoint);
            
            groupedAppend(out, number.substr(integralDigits + 1));

            // Pad with zeroes
            minDecimalDigits -= decimalDigits;
            while (minDecimalDigits-- > 0) {
                groupedAppend(out, zero);
            }
        }
        
        return out.join("");
    }
    
    function customNumberFormatter(number, format, radixPoint, thousandSeparator) {
        /// <summary>Handles formatting of custom numeric format strings.</summary>
        /// <param name="number" type="Number">The number to format.</param>
        /// <param name="format" type="String">A string specifying the format of the output.</param>
        /// <param name="radixPoint" type="String">The string that will be appended to the output as a radix point.</param>
        /// <param name="thousandSeparator" type="String">The string that will be used as a thousand separator of the integral digits.</param>
        /// <returns>The formatted value as a string.</returns>
        
        var digits = 0,
            forcedDigits = -1,
            integralDigits = -1,
            decimals = 0,
            forcedDecimals = -1,
            atDecimals = 0, // Bool
            unused = 1, // Bool, True until a digit has been written to the output
            c, i, f,
            format_length = format.length,
            endIndex,
            out = [];

        // Analyse format string
        // Count number of digits, decimals, forced digits and forced decimals.
        for (i = 0; i < format_length; i++) {
            c = format.charAt(i);
            
            // Check if we have reached a literal
            if (c == "'" || c == '"') {
                
                // Search for end of literal
                i = format.indexOf(c, i + 1);
                
                // If there is no matching end quotation mark, let's assume the rest of the string is a literal.
                // This is the way .NET handles things.
                if (i < 0) break;
                
            // Check for single escaped character
            } else if (c == "\\") {
                i++;
                
            } else {
            
                // Only 0 and # are digit placeholders, skip other characters in analyzing phase
                if (c == zero || c == "#") {
                    decimals += atDecimals;

                    if (c == zero) {
                        // 0 is a forced digit
                        if (atDecimals) {
                            forcedDecimals = decimals;
                        } else if (forcedDigits < 0) {
                            forcedDigits = digits;
                        }
                    }

                    digits += !atDecimals;
                }

                // If the current character is ".", then we have reached the end of the integral part
                atDecimals = atDecimals || c == ".";
            }
        }
        forcedDigits = forcedDigits < 0 ? 1 : digits - forcedDigits;

        // Negative value? Begin string with a dash
        if (number < 0) {
            out.push("-");
        }

        // Round the number value to a specified number of decimals
        number = numberToString(number, decimals);

        // Get integral length
        integralDigits = numberOfIntegralDigits(number);

        // Set initial number cursor position
        i = integralDigits - digits;

        // Initialize thousand grouping
        out.g = Math.max(integralDigits, forcedDigits);
        out.t = thousandSeparator;
        
        inString = 0;
        
        for (f = 0; f < format_length; f++) {
            c = format.charAt(f);
        
            // Check if we have reached a literal
            if (c == "'" || c == '"') {
                
                // Find end of literal
                endIndex = format.indexOf(c, f + 1);
                
                out.push(
                    format.substring(
                        f + 1, 
                        endIndex < 0 ? format.length : endIndex // assume rest of string if matching quotation mark is missing
                    ));
                
                if (endIndex < 0) break;
                f = endIndex;
            
            // Single escaped character
            } else if (c == "\\") {
                out.push(format.charAt(f + 1));
                f++;

            // Digit placeholder
            } else if (c == "#" || c == zero) {
                if (i < integralDigits) {
                    // In the integral part
                    if (i >= 0) {
                        if (unused) {
                            groupedAppend(out, number.substr(0, i));
                        }
                        groupedAppend(out, number.charAt(i));

                        // Not yet inside the number number, force a zero?
                    } else if (i >= integralDigits - forcedDigits) {
                        groupedAppend(out, zero);
                    }

                    unused = 0;

                } else if (forcedDecimals-- > 0 || i < number.length) {
                    // In the fractional part
                    groupedAppend(out, i >= number.length ? zero : number.charAt(i));
                }

                i++;

            // Radix point character according to current culture.
            } else if (c == ".") {
                if (number.length > ++i || forcedDecimals > 0) {
                    out.push(radixPoint);
                }

            // Other characters are written as they are, except from commas
            } else if (c !== ",") {
                out.push(c);
            }
        }
        
        return out.join("");
    }
    
    // ***** FORMATTERS
    // ***** Number Formatting *****
    _Number.prototype.__Format = function(format) {
        /// <summary>
        ///     Formats this number according the specified format string.
        /// </summary>
        /// <param name="format">The formatting string used to format this number.</param>

        var number = _Number(this),
            radixPoint = currentCulture._r,
            thousandSeparator = currentCulture._t;
        
        // If not finite, i.e. ±Intifity and NaN, return the default JavaScript string notation
        if (!isFinite(number)) {
            return "" + number;
        }
        
        // Default formatting if no format string is specified
        if (!format && format !== zero) {
            return basicNumberFormatter(number, 0, 0, 10, radixPoint);
        }
        
        // EVALUATE STANDARD NUMERIC FORMAT STRING
        // See reference at
        // http://msdn.microsoft.com/en-us/library/dwhawy9k.aspx
        
        var standardFormatStringMatch = format.match(/^([a-zA-Z])(\d*)$/);
        if (standardFormatStringMatch)
        {
            var standardFormatStringMatch_UpperCase = standardFormatStringMatch[1][toUpperCase](),
                precision = parseInt(standardFormatStringMatch[2], 10); // parseInt used to ensure empty string is aprsed to NaN
            
            // Limit precision to max 15
            precision = precision > 15 ? 15 : precision;
            
            // Standard numeric format string
            switch (standardFormatStringMatch_UpperCase) {
                case "D":
                    // DECIMAL
                    // Precision: number of digits
                    
                    // Note: the .NET implementation throws an exception if used with non-integral 
                    // data types. However, this implementation follows the JavaScript manner being
                    // nice about arguments and thus rounds any floating point numbers to integers.
                    
                    return basicNumberFormatter(number, numberCoalesce(precision, 1), 0, 0);
                
                case "F":
                    // FIXED-POINT
                    // Precision: number of decimals
                    
                    thousandSeparator = "";
                    // Fall through to N, which has the same format as F, except no thousand grouping
                    
                case "N":
                    // NUMBER
                    // Precision: number of decimals
                    
                    return basicNumberFormatter(number, 1, numberCoalesce(precision, 2), numberCoalesce(precision, 2), radixPoint, thousandSeparator);
                
                case "G":
                    // GENERAL
                    // Precision: number of significant digits
                    
                    // Fall through to E, whose implementation is shared with G
                    
                case "E":
                    // EXPONENTIAL (SCIENTIFIC)
                    // Precision: number of decimals
                    
                    // Note that we might have fell through from G above!
                    
                    // Determine coefficient and exponent for normalized notation
                    var exponent = 0, coefficient = Math.abs(number);
                    
                    while (coefficient >= 10) {
                        coefficient /= 10;
                        exponent++;
                    }
                    
                    while (coefficient < 1) {
                        coefficient *= 10;
                        exponent--;
                    }
                    
                    var exponentPrefix = standardFormatStringMatch[1],
                        exponentPrecision = 3,
                        minDecimals, maxDecimals;
                    
                    if (standardFormatStringMatch_UpperCase == "G") {
                        if (exponent > -5 && (!precision || exponent < precision)) {
                            minDecimals = precision ? precision - (exponent > 0 ? exponent + 1 : 1) : 0;
                            maxDecimals = precision ? precision - (exponent > 0 ? exponent + 1 : 1) : 10;
                        
                            return basicNumberFormatter(number, 1, minDecimals, maxDecimals, radixPoint);
                        }
                    
                        exponentPrefix = exponentPrefix == "G" ? "E" : "e";
                        exponentPrecision = 2;
                        
                        // The precision of G is number of significant digits, not the number of decimals.
                        minDecimals = (precision || 1) - 1;
                        maxDecimals = (precision || 11) - 1;
                    } else {
                        minDecimals = maxDecimals = numberCoalesce(precision, 6);
                    }
                    
                    // If the exponent is negative, then the minus is added when formatting the exponent as a number.
                    // In the case of a positive exponent, we need to add the plus sign explicitly.
                    if (exponent >= 0) {
                        exponentPrefix += "+";
                    }
                    
                    // Consider if the coefficient is positive or negative.
                    // (the sign was lost when determining the coefficient)
                    if (number < 0) {
                        coefficient *= -1;
                    }
                    
                    return basicNumberFormatter("" + coefficient, 1, minDecimals, maxDecimals, radixPoint, thousandSeparator) + exponentPrefix + basicNumberFormatter(exponent, exponentPrecision, 0);
                
                case "P":
                    // PERCENT
                    // Precision: number of decimals
                    
                    return basicNumberFormatter(number * 100, 1, numberCoalesce(precision, 2), numberCoalesce(precision, 2), radixPoint, thousandSeparator) + " %";
                
                case "X":
                    // HEXADECIMAL
                    // Precision: number of digits
                    
                    // Note: the .NET implementation throws an exception if used with non-integral 
                    // data types. However, this implementation follows the JavaScript manner being
                    // nice about arguments and thus rounds any floating point numbers to integers.
                    
                    var result = Math.round(number).toString(16);
                    
                    if (standardFormatStringMatch[1] == "X") {
                        result = result[toUpperCase]();
                    }
                    
                    // Add padding, remember precision might be NaN
                    precision -= result.length;
                    while (precision-- > 0) {
                        result = zero + result;
                    }
                    
                    return result;
                
                case "C":
                    // CURRENCY
                    // Precision: ignored (number of decimals in the .NET implementation)
                    
                    // The currency format uses a custom format string specified by the culture.
                    // Precision is not supported and probably won't be supported in the future.
                    // Developers probably use explicit formatting of currencies anyway...
                    format = currentCulture._c;
                    radixPoint = currentCulture._cr;
                    thousandSeparator = currentCulture._ct;
                    break;
                
                case "R":
                    // ROUND-TRIP
                    // Precision: ignored
                    
                    // The result should be reparsable => just use Javascript default string representation.
                    
                    return "" + number;
            }
        }
        
        // EVALUATE CUSTOM NUMERIC FORMAT STRING
                
        // Thousands
        if (format.indexOf(",.") !== -1) {
            number /= 1000;
        }

        // Percent
        if (format.indexOf("%") !== -1) {
            number *= 100;
        }

        // Split groups ( positive; negative; zero, where the two last ones are optional)
        var groups = format.split(";");
        if (number < 0 && groups.length > 1) {
            number *= -1;
            format = groups[1];
        } else {
            format = groups[!number && groups.length > 2 ? 2 : 0];
        }
        
        return customNumberFormatter(number, format, radixPoint, format.match(/^[^\.]*[0#],[0#]/) && thousandSeparator);
    };

    // ***** Date Formatting *****
    Date.prototype.__Format = function(format) {
        var date        = this, 
            year        = date.getFullYear(),
            month       = date.getMonth(),
            dayOfMonth  = date.getDate(),
            dayOfWeek   = date.getDay(),
            hour        = date.getHours(),
            minute      = date.getMinutes(),
            second      = date.getSeconds();
           
        // If no format is specified, default to G format
        format = format || "G";
        
        // Resolve standard date/time format strings
        if (format.length == 1) {
            format = currentCulture[format] || format;
        }
		
		return format.replace(/(\\.|'[^']*'|"[^"]*"|d{1,4}|M{1,4}|yyyy|yy|HH?|hh?|mm?|ss?|tt?)/g, 
			function (match) { 

                        // Day
                return match == "dddd" ? currentCulture._D[dayOfWeek] :
                                             // Use three first characters from long day name if abbreviations are not specifed
                        match == "ddd"  ? (currentCulture._d ? currentCulture._d[dayOfWeek] : currentCulture._D[dayOfWeek].substr(0, 3)) : 
                        match == "dd"   ? numberPair(dayOfMonth) :
                        match == "d"    ? dayOfMonth :
                        
                        // Month
                        match == "MMMM" ? currentCulture._M[month] :
                                             // Use three first characters from long month name if abbreviations are not specifed
                        match == "MMM"  ? (currentCulture._m ? currentCulture._m[month] : currentCulture._M[month].substr(0, 3)) :
                        match == "MM"   ? numberPair(month + 1) :
                        match == "M"    ? month + 1 :
                        
                        // Year
                        match == "yyyy" ? year :
                        match == "yy"   ? ("" + year).substr(2) :
                        
                        // Hour
                        match == "HH"   ? numberPair(hour) :
                        match == "H"    ? hour :
                        match == "hh"   ? numberPair((hour - 1) % 12 + 1) :
                        match == "h"    ? (hour - 1) % 12 + 1 :
                        
                        // Minute
                        match == "mm"   ? numberPair(minute) :
                        match == "m"    ? minute :
                        
                        // Second
                        match == "ss"   ? numberPair(second) :
                        match == "s"    ? second :
                        
                        // AM/PM
                        match == "tt"   ? (hour < 12 ? currentCulture._am : currentCulture._pm) : 
                        match == "t"    ? (hour < 12 ? currentCulture._am : currentCulture._pm).charAt(0) :
                        
                        // String literal => strip quotation marks
                        match.substr(1, match.length - 1 - (match.charAt(0) != "\\"));
			});
    };
    
    _String.__Format = function(str, obj0, obj1, obj2) {
        /// <summary>
        ///     Formats a string according to a specified formatting string.
        /// </summary>
        /// <param name="str">The formatting string used to format the additional arguments.</param>
        /// <param name="obj0">Object 1</param>
        /// <param name="obj1">Object 2 [optional]</param>
        /// <param name="obj2">Object 3 [optional]</param>

        var outerArgs = arguments;
        
        return str.replace(/(\{+)((\d+|[a-zA-Z_$]\w+(?:\.[a-zA-Z_$]\w+|\[\d+\])*)(?:\,(-?\d*))?(?:\:([^\}]*))?)(\}+)|(\{+)|(\}+)/g, function () {
            var innerArgs = arguments, value;
            
            // Handle escaped {
            return innerArgs[7] ? unescapeBraces(innerArgs[7]) :
            
            // Handle escaped }
                innerArgs[8] ? unescapeBraces(innerArgs[8]) :
            
            // Handle case when both { and } are present, but one or both of them are escaped
                innerArgs[1].length % 2 == 0 || innerArgs[6].length % 2 == 0 ?
                    unescapeBraces(innerArgs[1]) +
                    innerArgs[2] +
                    unescapeBraces(innerArgs[6]) :
            
            // Valid format item
                unescapeBraces(innerArgs[1], 1) +
                processFormatItem(innerArgs[3], innerArgs[4], innerArgs[5], outerArgs) +
                unescapeBraces(innerArgs[6], 1);
        });
    };

    // If a format method has not already been defined on the following objects, set __Format as format.
    var formattables = [ Date.prototype, _Number.prototype, _String ];
    for (var i in formattables) {
        formattables[i].format = formattables[i].format || formattables[i].__Format;
    }
    
    // Initiate culture
    updateCulture();
    
    return sffjs;
})(), 

// msf for backward compatibility
msf = sffjs;