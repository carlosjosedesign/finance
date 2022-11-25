const institutionModal = document.getElementById('institutionModal')

let editData 
const modalEdit = (id, element) => {
	const modal = document.querySelector(element.getAttribute("data-bs-target"))
	const modalButton = modal.querySelector('.modal-save')
	modalButton.dataset.id = id

	const nowName = document.querySelector(`#institution-${id} .name .value`).innerHTML.trim()
	const modalName = modal.querySelector('#institution-name')
	modalName.value = nowName
	modalName.placeholder = nowName

	editData = ['name'];
}


//Add institution buttons
institutionModal.querySelector('.btn-success').addEventListener('click', function (event) {
	event.preventDefault();
	const form = document.getElementById('add-institution-form')
 	postThis('institutions',form, institutionModal, 
	function (response) {
		// console.log(response)
		location.reload();
	}
	)
})
