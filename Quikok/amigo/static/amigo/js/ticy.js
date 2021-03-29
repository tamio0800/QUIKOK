//Onepage//
//偵測我們有幾個標點
$(document).ready(function () {
    var num_row = $(".pagearea").length

    //滾動滑鼠滾輪時，移動到上一頁、下一頁的效果
    n = 1
    moving = 0
    $(window).mousewheel(function (e) {
        $("html,body").stop()
        if (moving == 0) {
            moving = 1
            if (e.deltaY == -1) {
                if (n < num_row) {
                    n++
                }
            } else {
                if (n > 1) {
                    n--
                }
            }
        }
        $("html,body").animate({ "scrollTop": $(".page" + (n-1)).offset().top }, function () { moving = 0 })
        // console.log(n)
    })
// })

// //Topgo//
// $(function () {
    $(window).scroll(function () {
        if ($(this).scrollTop() > 240) {
            $("#gotop").fadeIn();
        } else {
            $("#gotop").fadeOut();
        }
    });
    $("#gotop").click(function () {
        n = 1
        $('body, html').animate({
            scrollTop: 0
        }, 30);
    });
});