
$(document).ready(function(){
	$(".AutoSuggestBox").jsonSuggest("/player/name_lookup/",{wildCard:'*',maxResults:10,ajaxResults:true,useJQueryAjax:true,JQueryAjaxParam : "text"})
//	$(".AutoSuggestBox").jsonSuggest(testData.fruits);
		
	});
