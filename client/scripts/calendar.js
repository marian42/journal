var calendar = $('.calendar')[0];
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
	while (calendar.firstChild) {
		calendar.removeChild(calendar.firstChild);
	}

	var currentYear = -1;
	var currentMonth = -1;
	var currentWeek = -1;
	var freshLine = true;
	var showMonth = false;

	if (data.first == null) {
		return;
	}

	var day = new Date(data.first[0], data.first[1] - 1, data.first[2]);
	var end = new Date(data.last[0], data.last[1] - 1, data.last[2]);

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

		element = addElement("div", "block day tooltip");
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

		var tooltip = document.createElement("span");
		tooltip.className = "tooltiptext";
		tooltip.innerText = monthNames[keyMonth - 1] + " " + keyDay + " (" + count + ")";
		element.appendChild(tooltip);

		if (count != 0) {
			let dayCopy = new Date(day.getTime());
			element.onclick = function() { jumpTo(dayCopy); };
		}

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

	calendar.scrollTo(0, calendar.scrollHeight);
}

function resetCalendar(filterInclude, filterTags) {
	$.ajax({url: "/api/days", data: {"include": filterInclude, "tags": JSON.stringify(filterTags) }, success: buildCalendar});
}
