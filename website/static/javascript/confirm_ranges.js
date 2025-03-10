let digits = '0123456789'

function enforceCharset(input_id, charset=digits){
	// set an event listener to an input and enforce that inputs are only from charset
	let targetInput = document.getElementById(input_id)
	targetInput.addEventListener("input", function() {
		let entered_value = targetInput.value.slice(-1)
		let pre_event_value = targetInput.value.slice(0,-1)
		if(!charset.includes(entered_value)){
			targetInput.value = pre_event_value;
			// special cases for lower/upper stuff
			let upper_case = entered_value.toLocaleUpperCase()
			let lower_case = entered_value.toLocaleLowerCase()
			if(charset.includes(upper_case)){
				targetInput.value += upper_case;
			} else if(charset.includes(lower_case)){
				targetInput.value = lower_case;
			}


		}
	});
}
