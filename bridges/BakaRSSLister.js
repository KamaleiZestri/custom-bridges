// ==UserScript==
// @name         BakaRSS Lister
// @namespace    https://github.com/KamaleiZestri/
// @version      1.0
// @description  Adds a download button to all list pages. Exports all manga in the list for use with BakaRSS.py
// @match        https://www.mangaupdates.com/lists/*
// @require      https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/1.3.8/FileSaver.min.js
// ==/UserScript==

function main()
{
    var exportBtn = document.getElementsByClassName("p-1 col-6")[0].children[1];
    var exportArea = document.getElementsByClassName("p-1 col-6")[0];



    var btn = document.createElement("button")
    btn.classList.add("button")
    btn.textContent = "RSS Export"


    exportArea.insertBefore(btn, exportBtn);

    btn.addEventListener("click", function ()
    {
        var saveData = {};

        var listData = document.querySelectorAll(".series-list-table_list_table__H2pQ5 > [class='row g-0']")
        for (var entry of listData)
        {
            var id = entry.getElementsByTagName("a")[0].href.match('/series/([0-9a-zA-Z]*)/')[1]
            var title = entry.getElementsByTagName("span")[0].innerHTML;
            saveData[id] = title;
        }

        var blob = new Blob([JSON.stringify(saveData)], { type: "application/json" });
        saveAs(blob, "bakareadinglist.json");
    });
}

// async function save(blob)
// {
//     var handle = await window.showSaveFilePicker();
//     var stream = await handle.createWritable();
//
//     await stream.write(blob);
//     await stream.close();
// }


(function() {
    //'use strict';
    setTimeout(main, 2000);
})();
