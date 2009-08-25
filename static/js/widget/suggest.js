
$(document).ready(function(){
	var params;
	if (typeof siteId === 'undefined')
	{
		params={};
		//alert('no site found');	
	}else{
		params={'site':siteId};
	}
	$(".AutoSuggestBox").jsonSuggest("/stat/player/name_lookup/",{wildCard:'*',maxResults:10,ajaxResults:true,useJQueryAjax:true,JQueryAjaxParam : "text",requestParams:params})
//	$(".AutoSuggestBox").jsonSuggest(testData.fruits);
	});
