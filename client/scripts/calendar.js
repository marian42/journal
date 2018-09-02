var calendar = $('.calendar')[0];
var monthNamesShort = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ];
var colorLimits = [0, 1, 5, 10, 20];

function addElement(tag, className) {
	var element = document.createElement(tag);
	if (className !== undefined) {
		element.className = className;
	}
	calendar.appendChild(element);
	return element;
}

function setColor(element, count) {
	for (var i = 0; i < colorLimits.length; i++) {
		if (count <= colorLimits[i]) {
			element.className += " shade" + i;
			return;
		}
	}
	element.className += " shade" + colorLimits.length;
}

function buildCalendar(data) {
	var currentYear = -1;
	var currentMonth = -1;
	var currentWeek = -1;
	var freshLine = true;
	var showMonth = false;

	var day = new Date(data.first[0], data.first[1] - 1, data.first[2]);
	var end = new Date(data.last[0], data.last[1] - 1, data.last[2]);

	if (!initializedTimeline) {
		initializeTimeline(day, end);
	}

	while (day < end) {
		if (day.getFullYear() != currentYear) {
			currentYear = day.getFullYear();
			yearElement = addElement("div", "year");
			yearElement.innerText = currentYear;
			freshLine = true;
		}

		if (day.getMonth() != currentMonth) {
			currentMonth = day.getMonth();
			showMonth = true;
		}

		if (freshLine) {
			for (var i = 0; i < day.getDay(); i++) {
				addElement("div", "block");
			}
			freshLine = false;
		}

		element = addElement("div", "block day");
		count = 0;
		keyYear = day.getFullYear()
		keyMonth = day.getMonth() + 1;
		keyDay = day.getDate();
		if (data.data[keyYear] != undefined
			&& data.data[keyYear][keyMonth] != undefined
			&& data.data[keyYear][keyMonth][keyDay] != undefined) {
				count = data.data[keyYear][keyMonth][keyDay];
			}
		setColor(element, count);
		var dayCopy = new Date(day);
		element.addEventListener('click', function() { jumpTo(dayCopy); });

		if (day.getDay() == 6) {
			addElement("br", "linebreak");
			freshLine = true;

			if (showMonth) {
				monthElement = addElement("div", "month");
				monthElement.innerText = monthNamesShort[currentMonth];
				showMonth = false;
			}
		}

		day.setDate(day.getDate() + 1);
	}
}

$.ajax({url: "/api/days", success: buildCalendar});
