(function($){
	$.fn.shuffle = function() {
	  return this.each(function(){
		var items = $(this).children();
		return (items.length)
		  ? $(this).html($.shuffle(items))
		  : this;
	  });
	}
  
	$.shuffle = function(arr) {
	  for(
		var j, x, i = arr.length; i;
		j = parseInt(Math.random() * i),
		x = arr[--i], arr[i] = arr[j], arr[j] = x
	  );
	  return arr;
	}
	  //Shuffle all rows, don't tpuch first column
	  //Requires: Shuffle
   $.fn.shuffleRows = function(){
	   return this.each(function(){
		  var main = $(/table/i.test(this.tagName) ? this.tBodies[0] : this);
		  var firstElem = [], counter=0;
		  main.children().each(function(){
			   firstElem.push(this.firstChild);
		   });
		  main.shuffle();
		  main.children().each(function(){
			 this.insertBefore(firstElem[counter++], this.firstChild); 
		  });
	   });
  }
	   })(jQuery);

$(document).ready(function(){
	$("#profiles > tbody").sortable({
		stop: function(x) {
		updateResults(calculateOLS());
	}});

	$("#profiles").shuffleRows();
})



function calculateOLS() {
	var attributes = [
		[0,0,1,1,1],
		[1,0,0,0,1],
		[0,0,0,0,1],
		[1,0,1,0,1],
		[1,1,1,0,1],
		[1,1,1,1,1],
		[0,0,0,1,1],
		[1,0,0,1,1],
		[0,1,0,1,1],
		[0,0,1,0,1],
		[0,1,1,0,1],
		[1,0,1,1,1],
		[0,1,0,0,1],
		[1,1,0,1,1],
		[1,1,0,0,1],
		[0,1,1,1,1],
	]
	
	var ranking = getRanking();
	
	var model=jStat.models.ols(ranking,attributes);

	return model.coef;
}

function getRanking() {
	var ranking = {

	}
	var counter = 0;
	$("#profiles tbody tr").each(function(x,y){
		console.log();
		ranking[$(y).children(":first-child").text()] = ++counter;
	});

	var result = [];
	console.log(Object.entries(ranking).sort());
	$.each(Object.entries(ranking).sort()
	,function(i,v){
		result.push(v[1])
	});

	console.log(result);

	return result;
}

function updateResults(coef) {
	$('#example').DataTable().destroy();
	console.log(coef);
    $('#example').DataTable( {
        data: [coef.map(function(x){
			return Math.round(x*100)/100.0
		})],
        columns: [
            { title: "Memory" },
            { title: "Screen size" },
            { title: "5G" },
            { title: "Price" },
            { title: "intersection" }
		],
		
		paging: false
    } );
}

function conjoint() {
	var coef = calculateOLS();


}

$(document).ready(function() {
	$.extend( $.fn.dataTable.defaults, {
		searching: false,
		ordering:  false,
		paging: false,
		"bInfo" : false
	} );
    $('#example').DataTable( {
        data: [],
        columns: [
            { title: "Memory" },
            { title: "Screen size" },
            { title: "5G" },
            { title: "Price" },
            { title: "intersection" }
        ]
	} );
	
	updateResults(calculateOLS());
} );