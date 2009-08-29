function setupSuggestBoxes()
{
	var params;
	if (typeof siteId === 'undefined')
	{
		params={};
	}else{
		params={'site':siteId};
	}   
	$(".AutoSuggestBox").jsonSuggest("/stat/player/name_lookup/",{wildCard:'*',maxResults:10,ajaxResults:true,useJQueryAjax:true,JQueryAjaxParam : "text",requestParams:params});
}


$(document).ready(function(){
		setupSuggestBoxes();
	});
