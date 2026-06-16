/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var showControllersOnly = false;
var seriesFilter = "";
var filtersOnlySampleSeries = true;

/*
 * Add header in statistics table to group metrics by category
 * format
 *
 */
function summaryTableHeader(header) {
    var newRow = header.insertRow(-1);
    newRow.className = "tablesorter-no-sort";
    var cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Requests";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 3;
    cell.innerHTML = "Executions";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 7;
    cell.innerHTML = "Response Times (ms)";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Throughput";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 2;
    cell.innerHTML = "Network (KB/sec)";
    newRow.appendChild(cell);
}

/*
 * Populates the table identified by id parameter with the specified data and
 * format
 *
 */
function createTable(table, info, formatter, defaultSorts, seriesIndex, headerCreator) {
    var tableRef = table[0];

    // Create header and populate it with data.titles array
    var header = tableRef.createTHead();

    // Call callback is available
    if(headerCreator) {
        headerCreator(header);
    }

    var newRow = header.insertRow(-1);
    for (var index = 0; index < info.titles.length; index++) {
        var cell = document.createElement('th');
        cell.innerHTML = info.titles[index];
        newRow.appendChild(cell);
    }

    var tBody;

    // Create overall body if defined
    if(info.overall){
        tBody = document.createElement('tbody');
        tBody.className = "tablesorter-no-sort";
        tableRef.appendChild(tBody);
        var newRow = tBody.insertRow(-1);
        var data = info.overall.data;
        for(var index=0;index < data.length; index++){
            var cell = newRow.insertCell(-1);
            cell.innerHTML = formatter ? formatter(index, data[index]): data[index];
        }
    }

    // Create regular body
    tBody = document.createElement('tbody');
    tableRef.appendChild(tBody);

    var regexp;
    if(seriesFilter) {
        regexp = new RegExp(seriesFilter, 'i');
    }
    // Populate body with data.items array
    for(var index=0; index < info.items.length; index++){
        var item = info.items[index];
        if((!regexp || filtersOnlySampleSeries && !info.supportsControllersDiscrimination || regexp.test(item.data[seriesIndex]))
                &&
                (!showControllersOnly || !info.supportsControllersDiscrimination || item.isController)){
            if(item.data.length > 0) {
                var newRow = tBody.insertRow(-1);
                for(var col=0; col < item.data.length; col++){
                    var cell = newRow.insertCell(-1);
                    cell.innerHTML = formatter ? formatter(col, item.data[col]) : item.data[col];
                }
            }
        }
    }

    // Add support of columns sort
    table.tablesorter({sortList : defaultSorts});
}

$(document).ready(function() {

    // Customize table sorter default options
    $.extend( $.tablesorter.defaults, {
        theme: 'blue',
        cssInfoBlock: "tablesorter-no-sort",
        widthFixed: true,
        widgets: ['zebra']
    });

    var data = {"OkPercent": 0.0, "KoPercent": 100.0};
    var dataset = [
        {
            "label" : "FAIL",
            "data" : data.KoPercent,
            "color" : "#FF6347"
        },
        {
            "label" : "PASS",
            "data" : data.OkPercent,
            "color" : "#9ACD32"
        }];
    $.plot($("#flot-requests-summary"), dataset, {
        series : {
            pie : {
                show : true,
                radius : 1,
                label : {
                    show : true,
                    radius : 3 / 4,
                    formatter : function(label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                            + label
                            + '<br/>'
                            + Math.round10(series.percent, -2)
                            + '%</div>';
                    },
                    background : {
                        opacity : 0.5,
                        color : '#000'
                    }
                }
            }
        },
        legend : {
            show : true
        }
    });

    // Creates APDEX table
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.0, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [0.0, 500, 1500, "TC-002-错误密码"], "isController": false}, {"data": [0.0, 500, 1500, "TC-004-空字段"], "isController": false}, {"data": [0.0, 500, 1500, "TC-007-SQL注入"], "isController": false}, {"data": [0.0, 500, 1500, "TC-005-记住我登录"], "isController": false}, {"data": [0.0, 500, 1500, "TC-008-XSS攻击"], "isController": false}, {"data": [0.0, 500, 1500, "TC-003-错误账号"], "isController": false}, {"data": [0.0, 500, 1500, "TC-009-重复登录设备B"], "isController": false}, {"data": [0.0, 500, 1500, "TC-010-超时后重新登录"], "isController": false}, {"data": [0.0, 500, 1500, "TC-001-成功登录"], "isController": false}]}, function(index, item){
        switch(index){
            case 0:
                item = item.toFixed(3);
                break;
            case 1:
            case 2:
                item = formatDuration(item);
                break;
        }
        return item;
    }, [[0, 0]], 3);

    // Create statistics table
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 9, 9, 100.0, 68.88888888888889, 49, 168, 59.0, 168.0, 168.0, 168.0, 13.274336283185841, 5.911227876106194, 3.2307222529498523], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["TC-002-错误密码", 1, 1, 100.0, 60.0, 60, 60, 60.0, 60.0, 60.0, 60.0, 16.666666666666668, 7.421875, 3.955078125], "isController": false}, {"data": ["TC-004-空字段", 1, 1, 100.0, 51.0, 51, 51, 51.0, 51.0, 51.0, 51.0, 19.607843137254903, 8.731617647058824, 4.384957107843138], "isController": false}, {"data": ["TC-007-SQL注入", 1, 1, 100.0, 49.0, 49, 49, 49.0, 49.0, 49.0, 49.0, 20.408163265306122, 9.088010204081632, 4.8828125], "isController": false}, {"data": ["TC-005-记住我登录", 1, 1, 100.0, 66.0, 66, 66, 66.0, 66.0, 66.0, 66.0, 15.151515151515152, 6.747159090909091, 3.832267992424242], "isController": false}, {"data": ["TC-008-XSS攻击", 1, 1, 100.0, 55.0, 55, 55, 55.0, 55.0, 55.0, 55.0, 18.18181818181818, 8.096590909090908, 4.971590909090909], "isController": false}, {"data": ["TC-003-错误账号", 1, 1, 100.0, 50.0, 50, 50, 50.0, 50.0, 50.0, 50.0, 20.0, 8.90625, 4.921875], "isController": false}, {"data": ["TC-009-重复登录设备B", 1, 1, 100.0, 59.0, 59, 59, 59.0, 59.0, 59.0, 59.0, 16.949152542372882, 7.547669491525424, 4.071769067796611], "isController": false}, {"data": ["TC-010-超时后重新登录", 1, 1, 100.0, 62.0, 62, 62, 62.0, 62.0, 62.0, 62.0, 16.129032258064516, 7.182459677419355, 3.8117439516129035], "isController": false}, {"data": ["TC-001-成功登录", 1, 1, 100.0, 168.0, 168, 168, 168.0, 168.0, 168.0, 168.0, 5.952380952380952, 2.650669642857143, 1.4357793898809523], "isController": false}]}, function(index, item){
        switch(index){
            // Errors pct
            case 3:
                item = item.toFixed(2) + '%';
                break;
            // Mean
            case 4:
            // Mean
            case 7:
            // Median
            case 8:
            // Percentile 1
            case 9:
            // Percentile 2
            case 10:
            // Percentile 3
            case 11:
            // Throughput
            case 12:
            // Kbytes/s
            case 13:
            // Sent Kbytes/s
                item = item.toFixed(2);
                break;
        }
        return item;
    }, [[0, 0]], 0, summaryTableHeader);

    // Create error table
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": [{"data": ["500", 1, 11.11111111111111, 11.11111111111111], "isController": false}, {"data": ["401", 8, 88.88888888888889, 88.88888888888889], "isController": false}]}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 9, 9, "401", 8, "500", 1, "", "", "", "", "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": ["TC-002-错误密码", 1, 1, "401", 1, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["TC-004-空字段", 1, 1, "401", 1, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["TC-007-SQL注入", 1, 1, "401", 1, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["TC-005-记住我登录", 1, 1, "401", 1, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["TC-008-XSS攻击", 1, 1, "401", 1, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["TC-003-错误账号", 1, 1, "401", 1, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["TC-009-重复登录设备B", 1, 1, "401", 1, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["TC-010-超时后重新登录", 1, 1, "401", 1, "", "", "", "", "", "", "", ""], "isController": false}, {"data": ["TC-001-成功登录", 1, 1, "500", 1, "", "", "", "", "", "", "", ""], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
