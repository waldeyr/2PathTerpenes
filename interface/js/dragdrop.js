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



/*window.sliderChange=function(val) {
	

		
    	document.getElementById('output').innerHTML = val;

    	var p="strat = (addSubset(eductMols) >> repeat["+val+"](inputRules))";
		  document.getElementById("resultado").innerHTML=p;
}
*/




window.ondblclick = function(event) {

  
  var modal = document.getElementById('id00');
  modal = document.getElementById('id01');
  
  if (event.target == modal) {
    modal.style.display = "none";
  }

}




window.addEventListener('click', function() {


  var check = document.querySelectorAll('input:checked');
  result.innerHTML = "result = mols[" + [].map.call(check, function(el){
  return el.value;
  }).join(',')+"]";
  
});




