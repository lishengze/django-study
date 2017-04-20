$(function () {
    console.log ('This is class Test!')

    var selectedNumb = 0;
    var sum_checkbox_id = 'action-toggle'
	var setNumbSelector = $('.paginator')
	var testCheckbox = 0;
    $(':checkbox').change(function(){            
		console.log(++testCheckbox);
        if ($(this).attr('id') === sum_checkbox_id) {
            if ($(this).is(':checked')) {				
                $('.action-select').each(function() {	
                    if (!$(this).is(':checked')) {
                    // if ($(this).attr('checked') !== 'checked') {
						console.log('Is action-toggle checked!')
						console.log ('')
                        $(this).attr("checked", true);
                        ++selectedNumb;
                        setNumbSelector.text(selectedNumb + ' 个被选中');
                    }
                });
            } else {				
                $('.action-select').each(function() {
                    if ($(this).is(':checked')) {
                    // if ($(this).attr('checked') === 'checked') {
						console.log('Is action-toggle unchecked!')
						console.log ('')
                        $(this).attr("checked", false);
                        --selectedNumb;
                        setNumbSelector.text(selectedNumb + ' 个被选中');
                    }
                });                    
            } 

            $('.action-select').each(function() {
                console.log ($(this).attr('checked'));
                console.log ($(this).is(':checked'));
            })
        } else {
            if ($(this).is(':checked')) {
                ++selectedNumb;
                $(this).attr("checked", true);
            } else {
                --selectedNumb;
                $(this).attr("checked", false);
            }
            setNumbSelector.text(selectedNumb + ' 个被选中');

            $('.action-select').each(function() {
                console.log ($(this).attr('checked'));
                console.log ($(this).is(':checked'));
            })
        } 
    })
});