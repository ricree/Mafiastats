function getSiteId()
{
	if (typeof siteId === 'undefined')
	{
		return null;
	}else
	{
		return siteId;
	}			
}
function setupSuggestBoxes()
{
	var params ={'site':getSiteId};
	$(".AutoSuggestBox").jsonSuggest("/stat/player/name_lookup/",{wildCard:'*',maxResults:10,ajaxResults:true,useJQueryAjax:true,JQueryAjaxParam : "text",requestParams:params});
}


$(document).ready(function(){
		setupSuggestBoxes();
	});
