// Theme
const light = document.querySelector('.choose-theme .light')
const dark = document.querySelector('.choose-theme .dark')

const setTheme = theme =>{
	if(theme == 'dark'){
		document.querySelector('body').classList.add('theme-dark')
        if(document.querySelector('.table')){
            document.querySelector('.table').classList = 'table table-dark table-striped'
        }
		light.classList.remove('active')
		dark.classList.add('active')
	}else{
		document.querySelector('body').classList.remove('theme-dark')
        if(document.querySelector('.table')){
            document.querySelector('.table').classList = 'table table-secondary  table-striped'
        }
		light.classList.add('active')
		dark.classList.remove('active')
	}

    let csrftoken = getCookie('csrftoken');
    fetch('setTheme', {
        method: "POST",
        body: JSON.stringify({
            theme: theme,
        }),
        headers: {"X-CSRFToken": csrftoken}
    })

	setCookie('theme',theme,7);
}

const refreshTheme = () => {
    const nowTheme = getCookie('theme')
    if(nowTheme == 'dark'){
        setTheme(nowTheme)
    }
}



const setCurrency = currency => {

    console.log(currency)
    document.querySelector(`.choose-currency input[value="${currency}"]`).classList.add('active')

    let csrftoken = getCookie('csrftoken');

    fetch('setCurrency', {
        method: "POST",
        body: JSON.stringify({
            currency: currency,
        }),
        headers: {"X-CSRFToken": csrftoken}
    })

    setCookie('currency',currency,7);
}

//Wallet
const setWallet  = value =>{
    if(value){
        document.querySelector('.eye.open').classList.remove('d-none')
        document.querySelector('.eye.close').classList.add('d-none')
        document.querySelectorAll('.blur').forEach(element =>{
            element.classList.remove('blur')
        })
    }else{
        document.querySelector('.eye.open').classList.add('d-none')
        document.querySelector('.eye.close').classList.remove('d-none')
        document.querySelectorAll('.with-blur').forEach(element =>{
            element.classList.add('blur')
        })
    }
}


// Cookies 
function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


//Monetary Currency Dictionary
const convertCurrency = currency => {
    if(currency == 'R$' || currency == 'BRL')
    return 'BRL'
    
    if(currency == '$' || currency == 'USD')
    return 'USD'
    
    if(currency == '€' || currency == 'EUR')
    return 'EUR'
    
    if(currency == '£' || currency == 'GBP')
    return 'GBP'
}

//Fields
const percentField = document.querySelectorAll('input[name=percent]')
if(percentField){
    percentField.forEach(field => {
        field.addEventListener('change', function(e){
            field.parentNode.querySelector('.percentage-declare').innerHTML = `${e.target.value}%`
        })
    })
   
}

//Stringfy data
function stringifyThis(form){
    let fd = new FormData(form);
    let data = {};
    for (let [key, prop] of fd) {
    data[key] = prop;
    }
    data = JSON.stringify(data, null, 2);
    return data
}

//Post Function
const postThis = (url, form, modal, _callback) => {
    let csrftoken = getCookie('csrftoken');

    fetch(url, {
        method: "POST",
        body: new FormData(form),
        headers: {"X-CSRFToken": csrftoken}
    })
    .then(response => response.json())
    .then(result => {
        // if success - update comment's content and relaod the page
        if (result.id) {

			const mymodal = bootstrap.Modal.getInstance(modal)
			mymodal.hide()
            
            _callback(result); 
        }
        else {
            console.log(result)
            for (let error in result.error) {
                console.log(error);
                document.querySelector(`input[name="${error}"]`).classList.add('is-invalid')
            }
            throw new Error(Object.keys(result.error)[0] + ' - ' + Object.values(result.error)[0]);                        
        }
    })
    .catch(error => {
        console.log(error)
        alert(error);
        // location.reload();
    })
}

//Edit Function
const editThis = (url, event, _callback) => {

    const form = document.getElementById(`edit-${url}-form`)
  
    let csrftoken = getCookie('csrftoken');
    // Send DELETE request
    fetch(`${url}/${event.target.dataset.id}`, {
        method: "PUT",
        body:   stringifyThis(form),
        headers: {"X-CSRFToken": csrftoken}
    })
    .then(async(response) => {
        // if success - update comment's content and relaod the page
        if (response.status === 204) {
            console.log(response)
            const thisElement =  document.querySelector(`#${url}-${event.target.dataset.id}`)
            console.log(thisElement)
            
            if(typeof editData  != "undefined"){
                editData.forEach(target => (
                    thisElement.querySelector(`.${target} .value`).innerHTML = document.getElementById(`${url}-${target}`).value
                ))
            }else{
                location.reload();
            } 

            const modal = document.getElementById(`modal_edit_${url}`)
            const mymodal = bootstrap.Modal.getInstance(modal)
            mymodal.hide()
            
        }
        // if error - show alert and reload the page
        else {
            console.log(response)
            let response_body = response.error
            for (let error in response_body.error) {
                console.log(error);
                document.querySelector(`input[name="${error}"]`).classList.add('is-invalid')
            }
            throw new Error(Object.keys(response_body.error)[0] + ' - ' + Object.values(response_body.error)[0]);                     
        }
    })
    .catch(error => {
        console.log(error)
        alert(error);
        // location.reload();
    })
}

//Delete Function
const modalDelete = (id, element) => {
	const modal = document.querySelector(element.getAttribute("data-bs-target"))
	const modalButton = modal.querySelector('.modal-delete')
	modalButton.dataset.id = id
}
const deleteThis = (url, event) => {
    let csrftoken = getCookie('csrftoken');

    // Send DELETE request
    fetch(`${url}/${event.target.dataset.id}`, {
        method: "DELETE",
        body: JSON.stringify({
            id: event.target.dataset.id,
        }),
        headers: {"X-CSRFToken": csrftoken}
    })
    .then(response => response.json())
    .then(result => {
        console.log(result)
        const modal = document.getElementById(`modal_delete_${url}`)
        const mymodal = bootstrap.Modal.getInstance(modal)
        mymodal.hide()

        if(result.success) {
            
            const thisElement =  document.querySelector(`#${url}-${event.target.dataset.id}`)
            thisElement.classList.add('hide')
            
            setTimeout(() => {
                thisElement.remove()
            },400)
            //location.reload()
        }
        // if error - show alert and reload the page
        else {
            let response_body = result.error
            for (let error in response_body.error) {
                console.log(error);
                document.querySelector(`input[name="${error}"]`).classList.add('is-invalid')
            }
            throw new Error(Object.keys(response_body.error)[0] + ' - ' + Object.values(response_body.error)[0]);                     
        }
    })
    .catch(error => {
        console.log(error)
        alert(error);
        // location.reload();
    })
}
