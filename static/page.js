String.Format = function() {
    if (arguments.length == 0)
        return "";
    if (arguments.length == 1)
        return arguments[0];
    var reg = /{(\d+)?}/g;
    var args = arguments;
    var result = arguments[0].replace(reg, function($0, $1) {
        return args[parseInt($1) + 1];
    })
    return result;
}
function QueryString(item) {
    var sValue = location.search.match(new RegExp("[\?\&]" + item + "=([^\&]*)(\&?)", "i"))
    return sValue ? sValue[1] : sValue
}


function RenderDynamicPager(recordCount, currentPage, pageSize, pagerID, param) {
    if (recordCount <= 0) return;
    var count = recordCount;
    var perpage = pageSize;
    var currentpage = currentPage
    var pagecount = Math.ceil(recordCount / pageSize);
    var pagestr = "";
    var breakpage = 3;
    var currentposition = 3;
    var breakspace = 2;
    var maxspace = 3;
    var prevnum = currentpage - currentposition;
    var nextnum = currentpage + currentposition;
    if (prevnum < 1) prevnum = 1;

    if (nextnum > pagecount) nextnum = pagecount;
    pagestr += (currentpage == 1) ? '<span class=\"current\">&laquo;</span>' : '<a href="' + String.Format(param, currentpage - 1) + '">&laquo;</a>';
    if (prevnum - breakspace > maxspace) {
        for (i = 1; i <= breakspace; i++)
            pagestr += '<a href="' + String.Format(param, i) + '">' + i + '</a>';
        pagestr += '<span class="break">...</span>';
        for (i = pagecount - breakpage + 1; i < prevnum; i++)
            pagestr += '<a href="' + String.Format(param, i) + '">' + i + '</a>';
    } else {
        for (i = 1; i < prevnum; i++)
            pagestr += '<a href="' + String.Format(param, i) + '">' + i + '</a>';
    }
    for (i = prevnum; i <= nextnum; i++) {
        pagestr += (currentpage == i) ? '<span class=\"current\">' + i + '</span>' : '<a href="' + String.Format(param, i) + '">' + i + '</a>';
    }
    if (pagecount - breakspace - nextnum + 1 > maxspace) {
        for (i = nextnum + 1; i <= breakpage; i++)
            pagestr += '<a href="' + String.Format(param, i) + '">' + i + '</a>';
        pagestr += '<span class="extend">...</span>';
        for (i = pagecount - breakspace + 1; i <= pagecount; i++)
            pagestr += '<a href="' + String.Format(param, i) + '">' + i + '</a>';
    } else {
        for (i = nextnum + 1; i <= pagecount; i++)
            pagestr += '<a href="' + String.Format(param, i) + '">' + i + '</a>';
    }
    pagestr += (currentpage == pagecount) ? '<span class=\"current\">&raquo;</span>' : '<a href="' + String.Format(param, currentpage + 1) + '">&raquo;</a>';
    pagestr += String.Format('<span class=\"pages\"> page {0} of total {1} pages. </span>', currentpage, pagecount);
    document.getElementById(pagerID).innerHTML = pagestr;
}


function RenderPager(recordCount, currentPage, pageSize,pagerID, func) {
    var count = recordCount;
    var perpage = pageSize;
    var currentpage = currentPage
    var pagecount = Math.ceil(recordCount / pageSize);
    var pagestr = "";
    var breakpage = 5;
    var currentposition = 2;
    var breakspace = 2;
    var maxspace = 4;
    var prevnum = currentpage - currentposition;
    var nextnum = currentpage + currentposition;
    if (prevnum < 1) prevnum = 1;

    if (nextnum > pagecount) nextnum = pagecount;
    pagestr += "<ul>";
    pagestr += (currentpage == 1) ? '<li class=\"disablepage\">&laquo;</li>' : '<li><a href="#1" onclick="javascript:' + String.Format(func, currentpage - 1) + '">&laquo;</a></li>';
    if (prevnum - breakspace > maxspace) {
        for (i = 1; i <= breakspace; i++)
            pagestr += '<li><a href="#1" onclick="javascript:' + String.Format(func, i) + '">' + i + '</a></li>';
        pagestr += '<span class="break">...</span>';
        for (i = pagecount - breakpage + 1; i < prevnum; i++)
            pagestr += '<li><a href="#1" onclick="javascript:' + String.Format(func, i) + '">' + i + '</a></li>';
    } else {
        for (i = 1; i < prevnum; i++)
            pagestr += '<li><a href="#1" onclick="javascript:' + String.Format(func, i) + '">' + i + '</a></li>';
    }
    for (i = prevnum; i <= nextnum; i++) {
        pagestr += (currentpage == i) ? '<li class=\"currentpage\">' + i + '</li>' : '<li><a href="#1" onclick="' + String.Format(func, i) + '">' + i + '</a></li>';
    }
    if (pagecount - breakspace - nextnum + 1 > maxspace) {
        for (i = nextnum + 1; i <= breakpage; i++)
            pagestr += '<li><a href="#1" onclick="javascript:' + String.Format(func, i) + '">' + i + '</a></li>';
        pagestr += '<span class="break">...</span>';
        for (i = pagecount - breakspace + 1; i <= pagecount; i++)
            pagestr += '<li><a href="#1" onclick="javascript:' + String.Format(func, i) + '">' + i + '</a></li>';
    } else {
        for (i = nextnum + 1; i <= pagecount; i++)
            pagestr += '<li><a href="#1" onclick="javascript:' + String.Format(func, i) + '">' + i + '</a></li>';
    }
    pagestr += (currentpage == pagecount) ? '<li class=\"disablepage\">&raquo;</li>' : '<li class=\"nextpage\"><a href="#1" onclick="' + String.Format(func, currentpage + 1) + '">&raquo;</a></li>';
    //pagestr += String.Format('<li class=\"disablepage\">{0}/{1} | {2}</li></ul>', currentpage, pageCount, recordCount);
    if (pagerID == '')
        return pagestr;
    document.getElementById(pagerID).innerHTML = pagestr;
}