var timeline = [];
var container = $('.timeline')[0];
var dayDividers = {}
var loadMoreIntervals = [];
var icons = ["whatsapp", "paypal", "money", "email", "facebook", "googleplay", "google", "twitter", "linkedin", "steam", "git", "wordpress", "kickstarter", "photo", "youtube", "reddit", "ebay"];

var filterTags = [];
var filterInclude = true;

Date.prototype.format = function() {
	var mm = this.getMonth() + 1;
	var dd = this.getDate();
	var hours = this.getHours();
	var minutes = this.getMinutes();
	return [(dd>9 ? '' : '0') + dd, (mm>9 ? '' : '0') + mm, this.getFullYear()].join('.') + " " + (hours < 10 ? "0" : "") + hours + ":" + (minutes < 10 ? "0" : "") + minutes;
};

Date.prototype.formatTime = function() {
	var hours = this.getHours();
	var minutes = this.getMinutes();
	return (hours < 10 ? "0" : "") + hours + ":" + (minutes < 10 ? "0" : "") + minutes;
};

class TimelineElement {
	constructor(time, element) {
		this.time = time;
		this.element = element;
		this.insert();
	}

	insert() {
		for (var i = 0; i < timeline.length; i++) {
			if (this.time <= timeline[i].time) {
				timeline.splice(i, 0, this);
				container.insertBefore(this.element, container.childNodes[i + 1]);
				return;
			}
		}

		timeline.push(this);
		container.appendChild(this.element);
	}

	remove() {
		timeline.splice(timeline.indexOf(this), 1);
		container.removeChild(this.element);
	}
}

class Event extends TimelineElement {
	constructor(dict) {
		var element = document.createElement("div");
		element.className = "event";
		var time = new Date(dict.time);
		time.add

		var timeDiv = document.createElement("div");
		timeDiv.innerText = time.formatTime();
		timeDiv.className = "time";
		element.appendChild(timeDiv);

		for (var icon of icons) {
			if (dict.tags.includes(icon)) {
				var iconDiv = document.createElement("div");
				iconDiv.className = "icon";
				iconDiv.style.backgroundImage = "url(/icons/" + icon + ".png)";
				element.appendChild(iconDiv);
				break;
			}
		}

		var messageDiv = document.createElement("div");
		messageDiv.innerText = dict.summary;
		messageDiv.className = "summary";
		element.appendChild(messageDiv);

		var tagsDiv = document.createElement("div");
		tagsDiv.className = "tags";
		element.appendChild(tagsDiv);

		for (var tag of dict.tags) {
			var tagSpan = document.createElement("span");
			tagSpan.className = "tag";
			tagSpan.innerText = tag;
			let tagCopy = tag;
			tagSpan.onclick = function() {
				addFilter(tagCopy);
			}
			tagsDiv.appendChild(tagSpan);
		}

		if (dict.url != null) {
			var tagSpan = document.createElement("a");
			tagSpan.innerText = dict.url;
			tagSpan.href = dict.url;
			tagsDiv.appendChild(tagSpan);
		}

		if (dict.images.length != 0) {
			var imagesDiv = document.createElement("div");
			imagesDiv.className = "images";
			element.appendChild(imagesDiv);
			for (var id of dict.images) {
				var link = document.createElement("a");
				link.href = "/api/image/" + id;
				var image = document.createElement("img");
				image.src = "/api/preview/" + id;
				link.appendChild(image);
				imagesDiv.appendChild(link);
			}
		}

		getDayDivider(time);
		time.setMilliseconds(10);
		super(time, element);
		this.data = dict;

		this.id = dict.id;
		this.expanded = false;
		var instance = this;
		messageDiv.addEventListener("click", function() { instance.click(); });
	}

	click() {
		if (this.expanded) {
			this.content.style.display = "none";
			this.expanded = false;
		} else {
			if (this.content != null) {
				this.content.style.display = "block";
				this.expanded = true;
			} else {
				var instance = this;
				$.ajax({url: "/api/details", data: {"id": this.id }, success: function(data) { instance.showDetails(data); }});
			}
		}
	}

	showDetails(data) {
		var container = document.createElement("div");
		container.className = "details";
		this.element.appendChild(container);

		for (var key in data) {
			var keyElement = document.createElement("div");
			keyElement.className = "key";
			keyElement.innerText = key;
			container.appendChild(keyElement);
			var valueElement = document.createElement("div");
			valueElement.className = "value";
			valueElement.innerText = data[key];
			container.appendChild(valueElement);
		}
		this.expanded = true;
		this.content = container;
	}
}

class LoadMore extends TimelineElement {
	constructor(time, forward) {
		var element = document.createElement("div");
		element.className = "loadMore";
		element.innerText = "Load more " + (forward ? "after" : "before") +  ": " + time.format();
		super(time, element);
		this.forward = forward;
		this.counterpart = null;
		var instance = this;
		element.addEventListener("click", function() { instance.load(); });

		if (forward) {
			loadMoreIntervals.push(this);
		}
	}

	setCounterpart(other) {
		this.counterpart = other;
		other.counterpart = this;
	}

	replace(data, scroll, callback) {
		var start = this.forward ? this.time : this.counterpart.time;
		var end = this.forward ? this.counterpart.time : this.time;
		var complete = data.length < 100;
		for (var dict of data) {
			var t = new Date(dict.time);
			if ((t >= start && !this.forward) || (t <= end && this.forward)) {
				var event = new Event(dict);
			} else {
				complete = true;
			}
		}

		if (complete) {
			this.remove();
			this.counterpart.remove();
		} else {
			this.remove();
			var newLoadMore = null;
			if (this.forward) {
				var t = new Date(data[data.length - 1].time);
				t.setMilliseconds(t.getMilliseconds() + 12);
				newLoadMore = new LoadMore(t, true);
			} else {
				var t = new Date(data[0].time);
				newLoadMore = new LoadMore(t, false);
			}
			newLoadMore.setCounterpart(this.counterpart);
		}

		container.scrollTo(0, this.forward ? scroll : container.scrollHeight - scroll);

		if (callback != null) {
			callback();
		}
	}

	load(callback) {
		var instance = this;
		var currentScroll = this.forward ? container.scrollTop : container.scrollHeight - container.scrollTop;
		$.ajax({url: "/api/events", data: {"time": this.time.getTime(), "before": !this.forward, "include": filterInclude, "tags": JSON.stringify(filterTags) }, success: function(data) { instance.replace(data, currentScroll, callback); }});
	}

	remove() {
		super.remove(this);
		if (this.forward) {
			loadMoreIntervals.splice(loadMoreIntervals.indexOf(this), 1);
		}
	}

	contains(time) {
		if (this.forward) {
			return this.time <= time && this.counterpart.time > time;
		} else {
			return this.time > time && this.counterpart.time <= time;
		}
	}

	split(time) {
		var start = this.forward ? this : this.counterpart;
		var end = this.forward ? this.counterpart : this;

		var timeForward = new Date(time);
		timeForward.setMilliseconds(timeForward.getMilliseconds() + 12);
		var newForward = new LoadMore(timeForward, true);
		var newBackward = new LoadMore(time, false);
		newForward.setCounterpart(end);
		newBackward.setCounterpart(start);

		return newForward;
	}
}

class DayDivider extends TimelineElement {
	constructor(time) {
		var element = document.createElement("div");
		element.className = "day";

		keyYear = time.getFullYear()
		keyMonth = time.getMonth() + 1;
		keyDay = time.getDate();

		element.innerText = daysOfTheWeek[time.getDay()] + ", " + monthNames[keyMonth - 1] + " " + keyDay + ", " + keyYear;
		time = new Date(keyYear, keyMonth - 1, keyDay);
		time.setMilliseconds(9);
		super(time, element);
		dayDividers[keyYear][keyMonth][keyDay] = this;
	}
}

function getDayDivider(day) {
	keyYear = day.getFullYear()
	keyMonth = day.getMonth() + 1;
	keyDay = day.getDate();
	if (dayDividers[keyYear] === undefined) {
		dayDividers[keyYear] = {};
	}
	if (dayDividers[keyYear][keyMonth] === undefined) {
		dayDividers[keyYear][keyMonth] = {};
	}
	if (dayDividers[keyYear][keyMonth][keyDay] === undefined) {
		return new DayDivider(day);
	}
	return dayDividers[keyYear][keyMonth][keyDay];
}

function scrollTo(year, month, day) {
	let startTime = new Date().getTime();
	let startScroll = container.scrollTop;
	(function step() {
		let currentTime = new Date().getTime();
		let progress = (currentTime - startTime) / 500;
		let endScroll =  dayDividers[year][month][day].element.offsetTop;
		if (progress > 1) {
			container.scrollTo(0, endScroll);
			return;
		}
		progress = 0.5 - 0.5 * Math.cos(progress * 3.14159);
		container.scrollTo(0, startScroll * (1 - progress) + endScroll * progress);
		setTimeout(step, 16);
	})();
}

function jumpTo(time) {
	let keyYear = time.getFullYear()
	let keyMonth = time.getMonth() + 1;
	let keyDay = time.getDate();
	if (dayDividers[keyYear] != undefined && dayDividers[keyYear][keyMonth] != undefined && dayDividers[keyYear][keyMonth][keyDay] != undefined) {
		scrollTo(keyYear, keyMonth, keyDay);
		return;
	}

	for (var item of loadMoreIntervals) {
		if (item.contains(time)) {
			var start = item.split(time);
			start.load(function() { scrollTo(keyYear, keyMonth, keyDay); });
			return;
		}
	}
}

var initializedTimeline = false;
function initializeTimeline() {
	initializedTimeline = true;

	while (container.firstChild) {
		container.removeChild(container.firstChild);
	}
	timeline = [];
	dayDividers = {}
	loadMoreIntervals = [];

	loadMoreStart = new LoadMore(new Date(0), true);
	loadMoreEnd = new LoadMore(new Date(), false);
	loadMoreStart.setCounterpart(loadMoreEnd);
	loadMoreEnd.load();
}

function updateFilter(include, tags) {
	$('.filter')[0].value = tags.join(" ");
	$('.topbar select')[0].value = include ? "with" : "without";
	filterTags = tags;
	filterInclude = include;

	initializeTimeline();
	resetCalendar(filterInclude, filterTags);
}

function addFilter(tag) {
	if (filterTags.includes(tag)) {
		return;
	}
	filterTags.push(tag);
	updateFilter(filterInclude, filterTags)
}

$('.filter')[0].onkeypress = function(event) {
	if (event.keyCode == 13) {
		var include = $('.topbar select')[0].value == "with";
		var tags = $('.filter')[0].value.replace(",", " ").split(" ");
		for (var i = 0; i < tags.length; i++) {
			tags[i] = tags[i].trim();
			if (tags[i].length == 0) {
				tags.splice(i, 1);
				i--;
			}
		}
		updateFilter(include, tags);
	}
}

initializeTimeline();
resetCalendar(true, []);
