(function($){
	$.fn.imageSelector = function(name,value){
		return this.each(function(){
		var selector =  $(this);
		var choiceInput = $("[name="+name+"]");
		selector.addClass("imageSelector-default");
		selector.addClass("ui-corner-all");
		selector.click(function(){
			$(".imageSelector-selected").removeClass("imageSelector-selected");
			selector.addClass("imageSelector-selected");
			selector.removeClass("imageSelector-default");
			choiceInput.val(value)});
	});
	}})(jQuery);
