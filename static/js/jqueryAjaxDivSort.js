var sortMethod;
var sortDirection;
var newDirection={'up':'down','down':'up'};
(function($){
	$.fn.ajaxDivSort = function(method,containerQuery,settings){
	var defaults = {};
	settings  = $.extend(defaults,settings);
	return this.each(function(){
		

	function parseUrl(url){
				var retval = {};
				var base = url.split('?');
				if(base.length>1){
					var params = base[1].split('&');
					for( var count in params){
						var temp = params[count].split('=');
						retval[temp[0]] = temp[1];
					}
				}
				retval = {'base':base[0],'args':retval};
				return retval;
			}
	
//will build and return a url
//base is a list where ['base'] is base url
//['args'] is a dict of GET parameters
	function buildUrl(base)
	{
	var url = parseUrl(base);
	var args = url.args
	args.method=sortMethod;
	args.direction = sortDirection;
	return (url.base+'?'+$.param(args));
	}

	function setPages()
	{
	$(".pageLink").each(function(obj){
		$(this).attr("href",buildUrl($(this).attr('href')));
	});
	}

	function sortBy(method)
	{
	if(method==sortMethod)
	{
		sortDirection=newDirection[sortDirection];
	}else{
		sortDirection='up';
		sortMethod=method;
	}
	setPages();
	$(containerQuery).load(buildUrl(window.location.toString()));
	}

	function setHighlight(){
	var elName = "#"+sortMethod+"Label";
	$('.colHeaderSelected').addClass('colHeaderNormal').removeClass('colHeaderSelected');
	$(elName).addClass('colHeaderSelected').removeClass('colHeaderHover').removeClass('colHeaderNormal');
	
	}
	var params = parseUrl(window.location.toString())['args'];
	if(typeof(sortMethod) == "undefined")
	{
		sortMethod = params.method;
		setHighlight();
		setPages();
	}
	if(typeof(sortDirection) == "undefined")
	{
		sortDirection = params.direction;
	}
	$(this).click(
		function()
		{
			sortBy(method);
			setHighlight();
		});
	$(this).mouseover(function(){
		$(this).filter('.colHeaderNormal').addClass('colHeaderHover').removeClass('colHeaderNormal');
		});
	$(this).mouseleave(function(){
			$(this).filter('.colHeaderHover').addClass('colHeaderNormal').removeClass('colHeaderHover');});
	});
}
})(jQuery);
