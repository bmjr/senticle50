/**
 * @author Stefanos Vichas
 * @repository https://github.com/svichas/wlcm
 *
 * The work in this class utlizes the base model of WLCM JS by Stefanos Vichas,
 * however has been adapted to work for strings rather than just words.
 *
 */
HTMLElement.prototype.wlcm = function (settings) {

    // initializing wlcm container
    var wlcm_contenaier = this;

    /* Setting settings default values */
    settings.min_speed = typeof settings.min_speed !== 'undefined' ? settings.min_speed : 2.97;
    settings.max_speed = typeof settings.max_speed !== 'undefined' ? settings.max_speed : 3;
    settings.font_size = 15;
    settings.word_buffer = 5;
    settings.words_on_screen = Math.floor((wlcm_contenaier.clientHeight - 17) / (settings.font_size + settings.word_buffer));

    // setting min speed
    if (settings.min_speed < 1) {
        settings.min_speed = 1;
    }


    // setting default element-css
    wlcm_contenaier.setAttribute("style", "position:relative;overflow:hidden;");

    var tops = [15 - (settings.font_size + settings.word_buffer), (wlcm_contenaier.clientHeight - 17 - (settings.font_size + settings.word_buffer))]
    var regions = getRegions(15, wlcm_contenaier.clientHeight - 17, tops)
    var i = 0;

    /**
     * Section to create words and append it to wlcm container
     */
    while (regions.length > 0) {
        // create word element
        var word_container = document.createElement("span");

        // setting id and html
        word_container.innerHTML = settings.words[i];
        word_container.id = "wlcm_element";

        // initializing starting top, speed and left
        var top = getRandomNumberForTops(15, wlcm_contenaier.clientHeight - 17, regions, tops);
        var left = getRandomNumber(-100, wlcm_contenaier.clientWidth, true);
        var speed = 3;

        // setting speed
        word_container.setAttribute("speed", speed);

        // setting default style
        word_container.setAttribute("style", "position:absolute;top:" + top + "px;display:inline-block;max-width:2000px;white-space:nowrap;font-size:15px;");

        // setting start left position
        word_container.style.left = left + "px";


        // appending word element to wlcm container
        wlcm_contenaier.appendChild(word_container);

        //Generate new regions
        regions = getRegions(15, wlcm_contenaier.clientHeight - 17, tops);
        i++;
    }


    /**
     * Clock to update position of words
     */
    setInterval(function () {


        // getting wlcm container children
        var word_nodes = wlcm_contenaier.children;


        // looping wlcm container children
        for (i = word_nodes.length - 1; i >= 0; i--) {


            // setting current node for each wlcm container children
            var current_node = word_nodes[i];

            // cleft for correct left position of current node
            var cleft = parseInt(current_node.style.left, 10);

            // getting current node starting speed from attribute
            var speed = current_node.getAttribute("speed");

            // updating left position of current node
            cleft -= speed;

            // if current node is offscreen go to end
            if (cleft < -current_node.clientWidth) {
                cleft = wlcm_contenaier.clientWidth;
                current_node.innerText = getNewString();
            }

            // updating left position of current node
            current_node.style.left = cleft + "px";

        }


    }, 50);


    /**
     * Function for random numbers
     */
    function getRandomNumber(min, max, int) {
        if (int) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        } else {
            return Math.random() * (max - min) + min;
        }
    }

    /**
     * Function for random tops
     */
    function getRandomNumberForTops(min, max, regions, existingTops) {
        top_region_index = Math.floor(Math.random() * Math.floor(regions.length - 1));
        top_value_index = Math.floor(Math.random() * Math.floor(regions[top_region_index].length - 1));
        top_value = regions[top_region_index][top_value_index];
        existingTops.push(top_value);
        return top_value;
    }

    function getRegions(min, max, existingTops) {
        //Descending list
        existingTops = existingTops.sort(function (a, b) {
            return a - b
        });

        if (existingTops.length == 0) {
            all_regions = [];
            for (j = min; j <= max + (settings.font_size + settings.word_buffer); j++) {
                all_regions.push(j);
            }
            return [all_regions];
        }

        regions = [];
        for (i = 0; i <= existingTops.length - 2; i++) {
            var current_top = existingTops[i];
            var next_top = existingTops[i + 1];

            space = Math.abs(next_top) - Math.abs(current_top);
            if (space < (settings.font_size + settings.word_buffer)) {
                continue;
            }
            new_region = []
            for (j = current_top + (settings.font_size + settings.word_buffer); j <= next_top - (settings.font_size + settings.word_buffer); j++) {
                new_region.push(j);
            }

            if (new_region.length > 0) {
                regions.push(new_region);
            }
        }
        return regions;
    }

    function getNewString() {
        found = false;
        var word_nodes = wlcm_contenaier.children;
        var strings_on_screen = [];
        for (i = 0; i <= word_nodes.length - 1; i++) {
            strings_on_screen.push(word_nodes[i].innerText);
        }
        var string;

        new_string_index = Math.floor(Math.random() * Math.floor(settings.words.length - 1));
        string = settings.words[new_string_index]

        return string;
    }

    return true;

};


