//adapted from http://www.djangosnippets.org/snippets/1389/
//original author: elo90ka

function updateElementIndex(el, prefix, ndx){
	var id_regex = new RegExp('(' + prefix + '-\\d+)');
	var replacement = prefix + '-' + ndx;
	if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
	if (el.id) el.id = el.id.replace(id_regex, replacement);
	if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function addForm(btn, prefix,context){
	if(context==null){
		context=$(document);
	}
	var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
	var row = $(".dynamic-form:first",context).clone(true);
	//alert("text" + $(row).hasClass('dynamic-form') + 'text');
	//alert($('.dynamic-form:first').html());
//	alert($(row).html());
//	$(row).insertAfter($('.dynamic-form:last'));
	//alert($(row).children().not(':last').html());
	$("*[name^="+prefix+"]",row).each(function() {
//		alert($(this).html());
		updateElementIndex(this, prefix, formCount);
		$(this).attr('checked',false).filter("[type!=checkbox]").val('').filter("option").remove();
		if ($(this).hasClass("NameBox")){
			$(this).empty();
		}
		
	});
	$("*[for^="+prefix+"]",row).each(function(){
		updateElementIndex(this,prefix,formCount);});
	$(row).find('.delete-row').click(function() {
		deleteForm(this, prefix);
	});
	$(row).insertAfter($('.dynamic-form:last',context));
	$('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
	return false;
}
function deleteForm(btn, prefix) {
	$(btn).parents('.dynamic-form').remove();
	var forms = $('.dynamic-form');
	$('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
	for (var i=0, formCount=forms.length; i<formCount; i++) {
		$(forms.get(i)).children().not(':last').children().each(function() {
			updateElementIndex(this, prefix, i);
		});
	}
	return false;
}


