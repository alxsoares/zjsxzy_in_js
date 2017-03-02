var data = source.data;
var filetext = '\ufeffDate, Absolute, Relative, Weighted\n';
for (i=0; i < data['date'].length; i++) {
    var currRow = [data['date'][i].toString(),
                   data['absolute'][i].toString(),
                   data['relative'][i].toString(),
                   data['weighted'][i].toString().concat('\n')];

    var joined = currRow.join();
    filetext = filetext.concat(joined);
}

var filename = 'data_result.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=gb2312;' });

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename);
}

else {
    var link = document.createElement("a");
    link = document.createElement('a')
    link.href = URL.createObjectURL(blob);
    link.download = filename
    link.target = "_blank";
    link.style.visibility = 'hidden';
    link.dispatchEvent(new MouseEvent('click'))
}
