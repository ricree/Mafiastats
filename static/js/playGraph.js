function loadGraph(dataSrc, selector,infoSelector){
	$.getJSON(dataSrc,function(dataset){

		var data = dataset.data;
		var initial  = dataset.initial;
		var infovis = $(selector);
		infovis.html('');
		var infobox = $(infoSelector);
		var w = infovis.innerWidth();
		var h = infovis.innerHeight();
		var centerx = w/2;
		var centery = h/2;
		var logBase = Math.log(10);
		var canvas = new Canvas('mycanvas', {'injectInto':'infovis',
			'width':w,
			'height':h});
		var ht = new RGraph(canvas, {
			levelDistance:225,
			Node:{color:"#f00000"},
			Edge:{overridable:true,color:"#008080"},
			onBeforePlotLine: function(adj){
				var pos1  = adj.nodeFrom.pos.toComplex();
				var pos2 = adj.nodeTo.pos.toComplex();
				var distx = Math.abs(pos1.x-pos2.x);
				var disty = Math.abs(pos1.y-pos2.y);
				if ((adj.nodeFrom.id == center) || (adj.nodeTo.id == center))
				{
					adj.data.$lineWidth = 1.6
					//adj.nodeTo.drawn = true;
					//adj.nodeFrom.drawn = true;
				}
				//else {adj.nodeTo.drawn = false;}
				else if ((distx>(w/2)) || (disty>(h/2))|| ((pos1.x*pos2.x < 0) && (pos1.y*pos2.y<0))){
					adj.data.$lineWidth = 0.01;
				}
				else{
					adj.data.$lineWidth = 0.3;
				}
			},
			onCreateLabel:function(domElement,node){
				domElement.innerHTML  = node.name;
				domElement.style.cursor = "pointer";
				domElement.onclick = function(){
					//var type = node.id[0];
					//var id = node.id.slice(1);
					//var url = "/stat/" + ((type=="p")?"player/":"team/") + id + "/graph/";
					var adjnodes = node.adjacencies;
					var nnodes = 0;
					for (var k in adjnodes){
						adjnodes[k].nodeTo.drawn = true;
						for (var l in adjnodes[k].nodeTo.adjacencies){
							adjnodes[k].nodeTo.adjacencies[l].nodeTo.drawn = true;
						}
						nnodes++;
					}
					//ht.levelDistance = 550 + (100*Math.log(nnodes) / logBase);
					center = node.id;
					infobox.html(node.data.infobox);
					ht.onClick(node.id,{hideLabels:false});
				};
			},
			onPlaceLabel: function(domElement, node){  
				 var style = domElement.style;  
				 style.display = '';  
				 style.cursor = 'pointer';  
		   
				 if (node._depth <= 1) {  
					 style.fontSize = "0.8em";  
					 style.color = "#ccc";  
				   
				 } else if(node._depth == 2){  
					style.display = 'none';
					 //style.fontSize = "0.7em";  
					 //style.color = "#494949";  
				   
				 } else {  
					 style.display = 'none';  
					node.drawn = false;
				 }  
		   
				 var left = parseInt(style.left);  
				 var w = domElement.offsetWidth;  
				 style.left = (left - w / 2) + 'px';  
			 }
		});
		ht.loadJSON(data,initial);
		var center = ht.root;
		ht.refresh();
		infobox.html(data[initial].data.infobox);
	});
}
