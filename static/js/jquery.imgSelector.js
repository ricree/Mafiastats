(function($){
	$.fn.imageSelector = function(name,value,callback){
		return this.each(function(){
		var selector =  $(this);
		var choiceInput = $("[name="+name+"]");
		var siblingClass= "imageSelector-name-"+name;
		selector.addClass("imageSelector-default");
		selector.addClass(siblingClass);
		selector.addClass("ui-corner-all");
		if (choiceInput.val() == value){
			selector.addClass("imageSelector-selected");
		}
		selector.click(function(){
			$(".imageSelector-selected."+siblingClass).addClass("imageSelector-default").removeClass("imageSelector-selected");
			selector.addClass("imageSelector-selected");
			selector.removeClass("imageSelector-default");
			choiceInput.val(value);
			if(callback){
				callback();
			}
			});
	});
	}})(jQuery);