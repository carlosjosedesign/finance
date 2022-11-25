let editBody, editID
const modalEdit = (id, element) => {
	const modal = document.querySelector(element.getAttribute("data-bs-target"))
	const modalButton = modal.querySelector('.modal-save')
	modalButton.dataset.id = id
	editID = id

	const nowAction = document.querySelector(`#transaction-${id} .action .value`).innerHTML
	const modalAction= modal.querySelector('#transaction-action')
	modalAction.value = nowAction

	const nowQuantity = document.querySelector(`#transaction-${id} .quantity .value`).innerHTML
	const modalQuantity= modal.querySelector('#transaction-quantity')
	modalQuantity.value = Number(nowQuantity.replace(',','.').replace(/[^0-9\.-]+/g,""));

	const nowPrice = document.querySelector(`#transaction-${id} .payprice .value`).innerHTML
	const modalPrice= modal.querySelector('#transaction-payprice')
	if( document.querySelector(`#transaction-${id} .payprice .currency`).innerHTML == 'R$'){
		nowPrice = nowPrice.replace(',','.').replace(/[^0-9\.-]+/g,"")
	}else{
		nowPrice = nowPrice.replace(/[^0-9\.-]+/g,"")
	}
	modalPrice.value = Number(nowPrice);

	const transactionDate = document.querySelector(`#transaction-${id} #transaction-flatpickr-date`).value
	const modalDate= modal.querySelector('#transaction-transaction_date')
	// console.log(transactionDate)
	
	let calendar = flatpickr(modalDate);
	calendar.setDate(transactionDate, "Y-m-d")

	modalDate.classList.add('form-control')

	editData = ['action','quantity','payprice', 'transaction_date'];
}

const editModal =  document.getElementById('modal_edit_transaction')
if(editModal != null) {
	editModal.addEventListener('hidden.bs.modal', function (event) {
		changeTotal()
	})
}


const changeTotal = () => {
	const thisLine = document.getElementById(`transaction-${editID}`)
	const nowQuantity = thisLine.querySelector('.quantity .value').innerHTML.replace(',','.')
	const nowPrice = thisLine.querySelector('.payprice .value').innerHTML.replace(',','.')

	const total = parseFloat(nowQuantity) * parseFloat(nowPrice)
	const totalprice = thisLine.querySelector('.totalprice .value')
	totalprice.innerHTML = total.toLocaleString('pt-br', {minimumFractionDigits: 2})
}

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const page_param = urlParams.get('i')
// console.log(page_param);

const newTransaction = () => {
	const transactionModal = document.getElementById('transactionModal')
	if(page_param){
		transactionModal.querySelector('#id_investiment').value = page_param
	}
}

//Filter Table
const selectTypeFilter = document.querySelector('#changeInvestiment select')

selectTypeFilter.addEventListener('change', function(event){
	const url = new URL(location.href);
	url.searchParams.set('i', event.target.value);

	location.assign(url.search);
})