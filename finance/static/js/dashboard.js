//Chart
const ctx = document.getElementById('myChart');

const chart = new Chart(ctx, {
	type: 'doughnut',
	data: {
		labels: [],
		datasets: [{
		  label: '%',
		  data: [],
		  backgroundColor: [],
		  borderWidth: 1
		}]
	},
	options: {
	  responsive: true,
	  plugins: {
		  legend: {
			  position: 'top',
		  },
	  }
	}
});


if(document.querySelector('#types-table') != null){	

	const typesLines = document.querySelectorAll('#types-table tbody tr:not(.hide)')

	newdata = {
		labels: [],
		datasets: [
		{
		  label: '%',
		  data: [],
		  backgroundColor: [],
		  borderWidth: 1
		},
		{
		  label: '%',
		  data: [],
		  backgroundColor: [],
		  borderWidth: 1
		},
		]
	}

	typesLines.forEach( typeLine => {
		var label = typeLine.querySelector('.name .value').innerHTML.trim()
		newdata.labels.push(label)
		
		var now_wallet = typeLine.querySelector('.now_wallet').innerHTML.replace('%','').replace(',','.')
		newdata.datasets[0].data.push(now_wallet)

		var go_wallet = typeLine.querySelector('.percent .value').innerHTML.replace('%','').replace(',','.')
		newdata.datasets[1].data.push(go_wallet)

		var color = typeLine.querySelector('.color').value
		newdata.datasets[0].backgroundColor.push(color)
		newdata.datasets[1].backgroundColor.push(color)
	})

	chart.data = newdata
    chart.update();
}

function updateOneChartData(i, data) {
	chart.data.labels[i] = data[0];
	chart.data.datasets[0].backgroundColor[i] = data[1];
	chart.data.datasets[1].backgroundColor[i] = data[1];
	chart.data.datasets[1].data[i] = data[2];
	chart.update();
}

//Block percentages to 100%
const changeMaxPercentage = ( ) =>{
	sumAllPercentages = 0
	lines =  document.querySelectorAll('.table tbody tr')
	lines.forEach( type =>{
		percent = type.querySelector('.percent .value').innerHTML.replace('%','')
		sumAllPercentages = sumAllPercentages + parseInt(percent)
	})
}
changeMaxPercentage()


let editBody, editID, removeID
const modalEdit = (id, element) => {
	const modal = document.querySelector(element.getAttribute("data-bs-target"))
	const modalButton = modal.querySelector('.modal-save')
	modalButton.dataset.id = id
	editID = id

	const nowName = document.querySelector(`#type-${id} .name .value`).innerHTML
	const modalName= modal.querySelector('#type-name')
	modalName.value = nowName

	const nowPercent = document.querySelector(`#type-${id} .percent .value`).innerHTML.replace('%','')
	const modalPercent = modal.querySelector('#id_percent')
	modalPercent.value = nowPercent
	modal.querySelector('.percentage-declare').innerHTML = nowPercent + '%'

	maxPercent = 100 - sumAllPercentages + parseInt(nowPercent)
	modalPercent.setAttribute("max", maxPercent)

	const nowColor = document.querySelector(`#type-${id} .color`).value
	const modalColor = modal.querySelector('#id_color')
	modalColor.value = nowColor

	editData = ['name'];

}

const changePercentageMax = percentage =>{
	lackPercent = 100 - percentage

	document.querySelectorAll('#typeModal #id_percent').forEach( input => {
		input.setAttribute("max", lackPercent);
		input.value =  lackPercent / 2;
		input.parentNode.querySelector('.percentage-declare').innerHTML = Math.round((lackPercent / 2), 2) + '%'
	})

}

const editModal =  document.getElementById('modal_edit_type')
if( editModal != null ){
	changePercentageMax(sumAllPercentages)

	editModal.querySelector('.modal-save').addEventListener('click', function (event) {
		const thisLine = document.getElementById(`type-${editID}`)
		percentage = document.getElementById('modal-percentage-declare').innerHTML
		thisLine.querySelector('.percent .value').innerHTML = percentage
		color = document.querySelector('#modal_edit_type #id_color').value
		thisLine.querySelector('.bgcolor').style.backgroundColor = color
		thisLine.querySelector('.color').value = color
		
		nameType = document.querySelector('#modal_edit_type #type-name').value

		changeMaxPercentage()
		changePercentageMax( sumAllPercentages )
		
		var nodes = Array.prototype.slice.call( document.querySelectorAll('#types-table tbody tr') )
		indexOfLine =  nodes.indexOf( thisLine )

		data = [nameType,color,percentage.replace('%','').replace(',','.')]

		updateOneChartData(indexOfLine, data);

	})
}

let removeIndex
const setRemoveItem = id => {
	removeID = id

	const thisLine = document.getElementById(`type-${removeID}`)

	var nodes = Array.prototype.slice.call( document.querySelectorAll('#types-table tbody tr') )
	removeIndex =  nodes.indexOf( thisLine )
}

const deleteModal =  document.getElementById('modal_delete_type')
if( deleteModal != null ){
	deleteModal.querySelector('.modal-delete').addEventListener('click', function (event) {
		
		chart.data.datasets[1].data[removeIndex] = 0;
		chart.update();

		setTimeout(() => {
			chart.data.labels = []
			const typesLines = document.querySelectorAll('#types-table tbody tr:not(.hide)')
			typesLines.forEach( typeLine => {
				var label = typeLine.querySelector('.name .value').innerHTML.trim()
				chart.data.labels.push(label)
			})
		
			chart.data = newdata
			chart.update();

		}, "500")

	})
}


const typeModal = document.getElementById('typeModal')
//Add type buttons
typeModal.querySelector('.btn-success').addEventListener('click', function (event) {
	event.preventDefault();
	const form = document.getElementById('add-type-form')
 	postThis('create_type',form, typeModal, 
	function (response) {
		location.reload();
	}
	)

})

const goalModal = document.getElementById('goalModal')
//Add type buttons
goalModal.querySelector('.btn-success').addEventListener('click', function (event) {
	event.preventDefault();
	const form = document.getElementById('add-goal-form')
 	postThis('create_goal',form, goalModal, 
	function (response) {
		// console.log(response)
		location.reload();
	}
	)
})



