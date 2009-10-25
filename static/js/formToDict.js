function formToDict(element){
	var el = $(element);
	var postArgs = {};
	$("input",el).filter("[type!=submit]").each(function(){
		var name = $(this).attr("name");
		var val = $(this).val();
		postArgs[name] = val;
	});
	$("select",el).each(function(){
		var selected = $("*:selected", this).val();
		if (typeof(selected) != "undefined"){
			var name = $(this).attr("name");
			postArgs[name] = selected;
		}
	});
	return postArgs;
}
