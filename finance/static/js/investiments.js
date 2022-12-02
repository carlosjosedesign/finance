const investimentModal = document.getElementById('investimentModal')
const transactionModal = document.getElementById('transactionModal')
const institutionModal = document.getElementById('institutionModal')
const typeModal = document.getElementById('typeModal')
const table = document.querySelector('.table')

//Transaction buttons
const addTransaction = (type, id) =>{
	transactionModal.querySelector('#id_action').value = type
	transactionModal.querySelector('#id_investiment').value = id
}

//Add institution buttons
institutionModal.querySelector('.btn-success').addEventListener('click', function (event) {
	event.preventDefault();
	const form = document.getElementById('add-institution-form')
 	postThis('institutions',form, institutionModal, 
	function (response) {
		// console.log(response)
		const newOption = document.createElement('option')
		newOption.value = response.id
		newOption.innerHTML = response.name
		document.querySelector('#id_institution').append(newOption)
		document.querySelector('#id_institution').value = response.id
	}
	)
})

//Add type buttons
typeModal.querySelector('.btn-success').addEventListener('click', function (event) {
	event.preventDefault();
	const form = document.getElementById('add-type-form')
	postThis('create_type',form, typeModal, 
	function (response) {
		// console.log(response)
		const newOption = document.createElement('option')
		newOption.value = response.id
		newOption.innerHTML = response.name
		document.querySelector('#id_type').append(newOption)
		document.querySelector('#id_type').value = response.id
		maxTypesPercentage = maxTypesPercentage - response.percent
	}
	)
})

typeModal.addEventListener('show.bs.modal', function (event) {
	// console.log(maxTypesPercentage)
	var percentageField = document.querySelector('#typeModal #id_percent')
	percentageField.setAttribute("max", maxTypesPercentage)
})


//Modal Edit
const modalEdit = (id, element) => {
	const modal = document.querySelector(element.getAttribute("data-bs-target"))
	const modalButton = modal.querySelector('.modal-save')
	modalButton.dataset.id = id

	const nowType= document.querySelector(`#investiment-${id} .type-id`).value
	const modalType= modal.querySelector('#id_type')
	modalType.value = nowType

	const nowInstitution= document.querySelector(`#investiment-${id} .institution-id`).value
	const modalInstitution= modal.querySelector('#id_institution')
	modalInstitution.value = nowInstitution

	const nowRating= document.querySelector(`#investiment-${id} .rating .value`).innerHTML.trim()
	const modalRating= modal.querySelector('#id_rating')
	modalRating.value = nowRating
}

let csrftoken = getCookie('csrftoken');

function newSync(){
	let codes = []
	lines = document.querySelectorAll('tbody tr')
	lines.forEach(function (line) {
		code = line.querySelector('.code .value').innerHTML.trim()
		currency = line.querySelector('.currency-symbol').value
		if(currency == 'R$'){
			codes.push(code + '.SA')
		}else{
			codes.push(code)
		}
		
	})
	// console.log(codes)

	fetch('get-prices', {
        method: "POST",
        body: JSON.stringify({
            codes: codes,
        }),
        headers: {"X-CSRFToken": csrftoken}
    })
    .then(response => response.json())
    .then(result => {
		// console.log(result)
		
		currenciesTotal = []
		currenciesLines = document.querySelectorAll('.moreTotalsWrapper .moreTotals .currencyTotal')

		currenciesLines.forEach(line => {
			currency = line.querySelector('strong').innerHTML.trim().replace(':','')
			currenciesTotal[currency] = 0
		})


		if(result.success){
			totalProducts = 0
			
			Object.entries(result.success).forEach(function([key, value]){
				// console.log(key, value);
				thisCode = key.replace('.SA', '')
				thisLine = document.querySelector(`.investiment-${thisCode}`)
				investimentPosition = thisLine.querySelector('.investiment-position').value
				lastedTrans = thisLine.querySelector('.investiment-lastedTrans').value
				currency = thisLine.querySelector('.currency-symbol').value
				quantity = parseFloat(thisLine.querySelector('.quantity .value').innerHTML.replace(',','.'))
				
				if(userCurrency == 'R$'){
					acquisition = parseFloat(thisLine.querySelector('.acquisition .value').innerHTML.replace('.','').replace(',','.').replace(currency,''))	
				}else{
					acquisition = parseFloat(thisLine.querySelector('.acquisition .value').innerHTML.replace(/[^0-9\.-]+/g,""))	
				}

				price = String(value).replace('.',',')
				// console.log(price)
				thisLine.querySelector('.nowprice .value').innerHTML = currency + ' ' + price

				if(quantity != 0){// is an active product
					revenue = value * quantity
					profit = ((revenue / acquisition ) - 1 ) * 100

					// console.log('acquisition', acquisition)
					// console.log(thisCode, profit)

					if(investimentPosition == 'SELL' ){
						if(lastedTrans == 'BUY'){
							if(acquisition > 0){
								profit = profit * -1
							}else{
								profit = profit + 100
							}
						}else{
							profit = profit * -1
						}
						
					}

					// Add parcial total
					currenciesTotal[currency] = currenciesTotal[currency] + revenue

					if(currency == userCurrency){
						totalProducts += revenue
					}else{
						currencyCode = convertCurrency(currency)
						currencyValue = parseFloat(document.querySelector(`#currencies-info .${currencyCode}`).innerHTML.replace(',','.').replace(userCurrency,''))
						userCurrencyRevenue = revenue * currencyValue
						totalProducts += userCurrencyRevenue
					}

					// console.log('quantity:' + quantity)
					// console.log('revenue:' + revenue)

					
					thisLine.querySelector('.revenue .value').innerHTML = coinFormat(revenue, currency)
					
					thisLine.querySelector('.profit .value').innerHTML =  String(parseFloat(profit.toFixed(2))).replace('.',',')
				}else{ //is an inactive productt
					
				}


			})
			Object.entries(result.success).forEach(function([key, value]){
				thisCode = key.replace('.SA', '')
				thisLine = document.querySelector(`.investiment-${thisCode}`)
				// console.log(totalProducts)
				quantity = parseFloat(thisLine.querySelector('.quantity .value').innerHTML.replace(',','.'))
				currency = thisLine.querySelector('.currency-symbol').value
				goPercent = parseFloat(thisLine.querySelector('.gowallet .value').innerHTML.replace('%',''))

				if(quantity != 0){// is an active product
					revenue = value * quantity

					if(currency != userCurrency){
						currencyCode = convertCurrency(currency)
						currencyValue = parseFloat(document.querySelector(`#currencies-info .${currencyCode}`).innerHTML.replace(',','.').replace(userCurrency,''))
						userCurrencyRevenue = revenue * currencyValue
						relatedTotal = totalProducts / currencyValue
						// console.log(relatedTotal)
						walletCurrency = goPercent * relatedTotal
					}else{
						walletCurrency = goPercent * totalProducts
						userCurrencyRevenue = revenue
					}

					walletCurrency = walletCurrency / 100

					inwallet = (userCurrencyRevenue / totalProducts) * 100

					toBuy = walletCurrency - revenue
					toBuyNum = toBuy / value
					
					thisLine.querySelector('.inwallet .value').innerHTML = String(parseFloat(inwallet.toFixed(2))).replace('.',',') + '%'
				
					thisLine.querySelector('.walletCurrency .value').innerHTML = coinFormat(walletCurrency, currency)
					thisLine.querySelector('.tobuy.currency .value').innerHTML = coinFormat(toBuy, currency)
					thisLine.querySelector('.tobuy.qnt .value').innerHTML =  parseFloat(toBuyNum.toFixed(2))
				}

			})

			//Change portfolio specific total
			// console.log(currenciesTotal)
			currenciesLines.forEach(line => {
				currency = line.querySelector('strong').innerHTML.trim().replace(':','')
				line.querySelector('span').innerHTML = coinFormat(currenciesTotal[currency], currency).replace(currency, '')
			})

			//Change portfolio all products total
			document.querySelector('.total .value').innerHTML =  coinFormat(totalProducts, userCurrency)
		

			const queryString = window.location.search;
			const urlParams = new URLSearchParams(queryString);
			const page_param = urlParams.get('type')
			if(!page_param){
				document.querySelector('#wallet .amount').innerHTML = coinFormat(totalProducts, userCurrency)
			}

		}
	})
}

function coinFormat (amount, currency){
	switch(currency){
		case '$':
			var currencyCode = 'USD'
			var locale = 'en-US'
		break;
		case 'R$':
			var currencyCode = 'BRL'
			var locale = 'pt-br'
		break;
		case '€':
			var currencyCode = 'EUR'
			var locale = 'de-DE'
		break;
		case '£':
			var currencyCode = 'GBP'
			var locale = 'GB'
		break;
	}
	
	if(amount > 0){
		return  amount.toLocaleString(locale, {style: 'currency', currency: currencyCode, minimumFractionDigits: 2, maximumFractionDigits:2})
	}else{
		return  amount.toLocaleString(locale, {style: 'currency', currency: currencyCode, minimumFractionDigits: 2, maximumFractionDigits:2})
	}
}

function startSync(){
	setInterval( () =>{ newSync(); } ,5000)
	// setTimeout( () =>{ console.log('new iteration'); newSync(); } ,5000)
}

function delaySync(){
	// console.log('new start')
	if( document.querySelectorAll('tbody tr').length > 0){
		setTimeout( startSync() ,3000)
	}
	
}
delaySync();


//Filter Table
const selectTypeFilter = document.querySelector('#changeType select')

if(selectTypeFilter != null){
selectTypeFilter.addEventListener('change', function(event){
	const url = new URL(location.href);
	url.searchParams.set('type', event.target.value);

	location.assign(url.search);
})
}

var selections = ['rating','acquisition','profit','walletCurrency','tobuy'];
var checkboxElems = document.querySelectorAll("#tableColumns input[type='checkbox']");

for (var i = 0; i < checkboxElems.length; i++) {
  checkboxElems[i].addEventListener("click", displayCheck);
}

function displayCheck(e) {
	if (e.target.checked) {
		selections.push(e.target.value)
	} 
	else {
		let start = selections.indexOf(e.target.value);
		selections.splice(start, 1);
	}

	// console.log(selections)

	var ratingrows = table.querySelectorAll('.rating')
	var acquisitionrows = table.querySelectorAll('.acquisition')
	var profitrows = table.querySelectorAll('.profit')
	var walletrows = table.querySelectorAll('.gowallet, .inwallet')
	var walletCurRows = table.querySelectorAll('.walletCurrency')
	var tobuyrows = table.querySelectorAll('.tobuy')
	var institutionrows = table.querySelectorAll('.institution')

	if(selections.includes('rating')){
		ratingrows.forEach(function(row){ row.style.display="table-cell"})
	}else{
		ratingrows.forEach(function(row){ row.style.display="none"})
	}

	if(selections.includes('acquisition')){
		acquisitionrows.forEach(function(row){ row.style.display="table-cell"})
	}else{
		acquisitionrows.forEach(function(row){ row.style.display="none"})
	}

	if(selections.includes('profit')){
		profitrows.forEach(function(row){ row.style.display="table-cell"})
	}else{
		profitrows.forEach(function(row){ row.style.display="none"})
	}

	if(selections.includes('wallet')){
		walletrows.forEach(function(row){ row.style.display="table-cell"})
	}else{
		walletrows.forEach(function(row){ row.style.display="none"})
	}

	if(selections.includes('walletCurrency')){
		walletCurRows.forEach(function(row){ row.style.display="table-cell"})
	}else{
		walletCurRows.forEach(function(row){ row.style.display="none"})
	}

	if(selections.includes('tobuy')){
		tobuyrows.forEach(function(row){ row.style.display="table-cell"})
	}else{
		tobuyrows.forEach(function(row){ row.style.display="none"})
	}

	if(selections.includes('institution')){
		institutionrows.forEach(function(row){ row.style.display="table-cell"})
	}else{
		institutionrows.forEach(function(row){ row.style.display="none"})
	}

	var actionsrows = table.querySelectorAll('.actions')

	if(selections.length > 5){
		actionsrows.forEach(function(row){ row.style.display="none"})
	}else{
		actionsrows.forEach(function(row){ row.style.display="table-cell"})
	}
}

//Mobile
function openInvestimentInfo(id){
	const line = document.querySelector(`#investiment-${id}`)
	// console.log(line)
	line.classList.toggle('show')
}