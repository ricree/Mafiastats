function formToDict(element){
	var el = $(element);
	var postArgs = {};
	$("input",el).filter("[type!=submit]").each(function(){
		var name = $(this).attr("name");
		var val = $(this).val();
		postArgs[name] = val;
	});
	$("select",el).each(function(){
		var selected = $("*:selected", this);
		var val;
		if (typeof(selected) != "undefined"){
			var mult = $(this).attr("multiple");
			if($(this).attr("multiple")==true){
				val = [];
				selected.each(function(){
					val.push($(this).val());
				});
			}else{
				val = selected.val();
			}
				var name = $(this).attr("name");
				postArgs[name] = val
		}
	});
	return postArgs;
}
