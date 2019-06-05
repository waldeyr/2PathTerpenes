window.dragStart = function(e) {

      e.dataTransfer.setData("Text", e.target.id);

}

window.allowDropOption = function(e) { 
        e.preventDefault(); 
}

window.drop = function(e) {
  
    e.preventDefault();
    var data = e.dataTransfer.getData("text");
    var nodeCopy = document.getElementById(data).cloneNode(true);
    e.target.appendChild(nodeCopy);
  
    var txt1 = e.target.appendChild(nodeCopy);
    txt1.onclick = function() {
    this.remove();}

}

window.saveAndDisplay = function() {
  var list = document.getElementById('dropBox').children;
  var result="";
  for (var i = 0; i < list.length; i++) {
    result +="<br/>"+"&nbsp;"+list[i].id+"<br/>";
  }
  document.getElementById('demo').innerHTML=result;
}




window.getNumber = function() {  

		var number=document.getElementById("number").value; 
	
		var p;
    p="<br/>"+"strat = (addSubset(eductMols) >> repeat["+number+"](inputRules))"+"<br/>";
		document.getElementById("resultado").innerHTML=p;
		
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

	if(x=="result = mols[]"){
		result.innerHTML="";
    
	}
     
          
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
