function CopyToBox(node)
{
	return function(item){
	var box = $(node).children(":last").get(0);
	var textField = $(node).children(":first").get(0);
	if(textField.value!=""){ //makes sure to only do this once
		var names = new Array();
		nameList  = String(textField.value);
		names = nameList.split(',');
		for (var n in names)
		{
			box.add(new Option(names[n],names[n]),null);
		}
		$(textField).val("")};
	}
}
function CopyToResult(source,dest)
{
//	alert("registered "+source);
	return function(){
//		alert("called");
		var result = source.options;
		var outp = "";
		if(result != undefined)
		{
			for(var i=0;i<source.length;i++)
			{
				if(i!=0){
					outp+=',';
				}
				outp+=result[i].text;
			}
		}
		dest.value = outp;
//;		alert(dest.value);
	}
}
	
function SetChooser()
{	
	$(".NameBox").each(function(){
		$(this).unbind();
		});
	$(".NameBoxText").each(function(){
		$(this).unbind();
		});
	//set the autocomplete on the text box with a callback to insert text into list when a name is chosen
	$(".NameChooser").each(function(){
			var node = this;
			var params={'site':function(){return siteId;}};
			$(this).children(":first").jsonSuggest("/stat/player/name_lookup/",{wildCard:'*',maxResults:10,ajaxResults:true,useJQueryAjax:true,requestParams:params,JQueryAjaxParam : "text",onSelect:CopyToBox(node)}).keyup(function(e){
	if(e.which == 0xD){
		CopyToBox(node)(null);
	}
	});
			var src = $(node).children("select").get(0);
			var dest = $(node).children("#team_result").get(0);
			$(src.option).change(CopyToResult(src,dest));
			$("form").submit(CopyToResult(src,dest));
			//alert("hi");

	
		/*function(item){
		var box = $(node).children(":last").get(0);
		var textField = $(node).children(":first").get(0);
//	alert($(box).attr('id'));
		box.add(new Option(item.text, item.text),null);
		$(textField).val("")
		}}*/
		});
		//)});
		$(".NameBox").each(function(){
				$(this).contextMenu({
				menu: 'nameMenu'},
				function(action,el,pos){
					if(action == 'remove'){
						var box = $(el).parent().children(":last").get(0);
						while(box.selectedIndex >-1){
							box.remove(box.selectedIndex);
						}
					}
	})})
}
$(document).ready(SetChooser).ready(function(){
	$("#populate_fake").click(function(){
		$(".NameChooser").each(function(){
			node = this;
			var src = $(node).children("select").get(0);
            var dest = $(node).children("#team_result").get(0);
//			alert(src);
//			alert(dest);
			CopyToResult(src,dest)();
			})
		})
	});
