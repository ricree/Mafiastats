
$(document).ready(function(){
	$(".AutoSuggestBox").jsonSuggest("http://localhost:8000/player/name_lookup/",{wildCard:'*',maxResults:10,ajaxResults:true,useJQueryAjax:true,JQueryAjaxParam : "text"})
//	$(".AutoSuggestBox").jsonSuggest(testData.fruits);
		
	});
