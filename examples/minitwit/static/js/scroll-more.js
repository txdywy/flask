/******************************************
    Infinite jQuery Scroll
    @author Fabio Mangolini
    http://www.responsivewebmobile.com
******************************************/
jQuery(document).ready(function() {
    //location.href = 'index.html#start';
    var page;
    var loaded = new Array(); //key value array to prevent loading a page more than once
    var index = 1;
    var more = 1;

    //get all the pages link inside the #pages div and fill an array
    $('#pages a').each(function(i) {
        page = $(this).attr('href');
        loaded[1] = 0;
        //pages[index] = $(this).attr('href');
        //loaded[$(this).attr('href')] = 0; //initialize all the pages to be loaded to 0. It means that they are not yet been loaded.
    });

    //on scroll gets when bottom of the page is reached and calls the function do load more content
    $(window).scroll(function(e){
        //Not always the pos == h statement is verified, expecially on mobile devices, that's why a 300px of margin are assumed.
        /*
        if($(window).scrollTop() + $(window).height() >= $(document).height() - 300) {
            console.log("bottom of the page reached!");

            //in some broswer (es. chrome) if the scroll is fast, the bottom 
            //reach events fires several times, this may cause the page loaging 
            //more than once. To prevent such situation every time the bottom is 
            //reached the number of time is added to that page in suach a way to call 
            //the loadMoreContent page only when the page value in "loaded" array is 
            //minor or equal to one
            loaded[pages[current+1]] = loaded[pages[current+1]] + 1; 
            console.log(loaded)
            if(loaded[pages[current+1]] <= 1)
                loadMoreContent(current+1);
        }
        */
        if ($(window).scrollTop() <= 0) {
            console.log("top of the page reached!");
            loaded[index] = loaded[index] + 1
            if(more===1 && loaded[index] <= 1){         
                loadMoreContent(index);
                index = index + 1;
                loaded[index] = 0;
            }
        }
    });

    //loads the next page and append it to the content with a fadeIn effect. 
    //Before loading the content it shows and hides the loaden Overlay DIV
    function loadMoreContent(position) {
        /*
        //try to load more content only if the counter is minor than the number of total pages
        if(position < pages.length) {
            $('#loader').fadeIn('slow', function() {
                $.get(pages[position], function(data) {
                    $('#loader').fadeOut('slow', function() {
                        $('#scroll-container').prepend(data).fadeIn(999);
                        current=position;
                    });
                });
            });
        }
        */
        $('#loader').fadeIn('slow', function() {
            $.get(page + '&index=' + index, function(data) {
                if (data === ''){
                    more = 0;
                }
                $('#loader').fadeOut('slow', function() {
                    $('#scroll-container').prepend(data).fadeIn(999);
                    index = index + 1;
                    loaded[index] = 0;
                });
            });
        });
    }
});
