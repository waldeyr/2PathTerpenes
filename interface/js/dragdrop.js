window.dragStart = function(e) {
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("Text", e.target.getAttribute("id"));
}
window.allowDropOption = function(e) {
    e.preventDefault();
    
}



var list;
list = document.getElementById('dropBox').children;

window.saveAndDisplay = function() {


var list = document.getElementById('dropBox').children;
  var result="";
  for (var i = 0; i < list.length; i++) {
    result +="<br/>"+list[i].id+"<br/>";
  }
  document.getElementById('rules').innerHTML=result;
  
}


window.drop = function(e) {
      
      
      //e.preventDefault();
    var data = e.dataTransfer.getData("text");
    var nodeCopy;
    nodeCopy = document.getElementById(data).cloneNode(true);
    
    for (var i = 0; i < list.length; i++) {
        var r = list[i].id;
        if(data == r)  {
        
          nodeCopy = document.getElementById(data).cloneNode(false);
          this.remove(list[i].id);
        }
    }
  
    var txt1 = e.target.appendChild(nodeCopy);
    txt1.onclick = function() {
      this.remove();}
 
   
}




window.getNumber = function() {  

		var number=document.getElementById("number").value; 
	
		var x;
    x="<br/>"+"strat = (addSubset(eductMols) >> repeat["+number+"](inputRules))"+"<br/>";
		document.getElementById("interations").innerHTML=x;
		
}




window.ondblclick = function(event) {

}




$('input[type="checkbox"]').on("click", checkBox);


function  checkBox(){
    var check;
  
  check = document.querySelectorAll('input:checked');
 	 
	var x = result.innerHTML = "eductMols = [" + [].map.call(check, function(el){

	return el.value;
	}).join(',')+"]";

	
     
          
}



$('#modal').modal({
  show: false
});

$('button').on('dblclick', function() {
	var x =  $(this).attr('id');
  //alert(x);
  if(x=="0r"){
    $('#modal0').modal('show');
  }
  if(x=="1r"){
    $('#modal1').modal('show');
  }

  if(x=="2r"){
    $('#modal2').modal('show');
  }
  if(x=="3r"){
    $('#modal3').modal('show');
  }

  if(x=="4r"){
    $('#modal4').modal('show');
  }
  if(x=="5r"){
    $('#modal5').modal('show');
  }

  if(x=="6r"){
    $('#modal6').modal('show');
  }
  if(x=="7r"){
    $('#modal7').modal('show');
  }

  if(x=="8r"){
    $('#modal8').modal('show');
  }
  if(x=="9r"){
    $('#modal9').modal('show');
  }

  if(x=="10r"){
    $('#modal10').modal('show');
  }
  if(x=="11r"){
    $('#modal11').modal('show');
  }

  if(x=="12r"){
    $('#modal12').modal('show');
  }
  if(x=="13r"){
    $('#modal13').modal('show');
  }

  if(x=="14r"){
    $('#modal14').modal('show');
  }
  if(x=="15r"){
    $('#modal15').modal('show');
  }

  if(x=="16r"){
    $('#modal16').modal('show');
  }
  if(x=="17r"){
    $('#modal17').modal('show');
  }


});



function download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

// Start file download.
document.getElementById("dwn-btn").addEventListener("click", function(){
    // Generate download of hello.txt file with some content
    var text = document.getElementById("corpo").innerText;
    var filename = "simulation.py";
    
    download(filename, text);
}, false);
