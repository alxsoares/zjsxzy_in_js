var data = source.data;
var filetext = '\ufeff组合,单位净值,今年以来业绩,成立以来业绩,最大回撤,夏普率,波动率\n';
for (i=0; i < data['name'].length; i++) {
    var currRow = [data['name'][i].toString(),
                   data['net value'][i].toString(),
                   data['year return'][i].toString(),
                   data['total return'][i].toString(),
                   data['max drawdown'][i].toString(),
                   data['sharpe'][i].toString(),
                   data['volatility'][i].toString().concat('\n')];

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
