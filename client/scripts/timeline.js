var timeline = [];
var container = $('.timeline')[0];

Date.prototype.format = function() {
  var mm = this.getMonth() + 1;
  var dd = this.getDate();
  var hours = this.getHours();
  var minutes = this.getMinutes();
  return [(dd>9 ? '' : '0') + dd, (mm>9 ? '' : '0') + mm, this.getFullYear()].join('.') + " " + (hours < 10 ? "0" : "") + hours + ":" + (minutes < 10 ? "0" : "") + minutes;
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
		super(new Date(dict.time), element);
		element.innerText = this.time.format() + " " + dict.summary;
		this.data = dict;
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
	}

	setCounterpart(other) {
		this.counterpart = other;
		other.counterpart = this;
	}

	replace(data) {
		var start = this.forward ? this.time : this.counterpart.time;
		var end = this.forward ? this.counterpart.time : this.time;
		var complete = data.length < 100;
		for (var event of data) {
			var t = new Date(event.time);
			if ((t >= start && !this.forward) || (t <= end && this.forward)) {
				new Event(event);
			} else {
				console.log("outside " + t + ", " + start + " - " + end);
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
				t.setMilliseconds(t.getMilliseconds() + 1);
				newLoadMore = new LoadMore(t, true);
			} else {
				var t = new Date(data[0].time);
				t.setMilliseconds(t.getMilliseconds() - 1);
				newLoadMore = new LoadMore(t, false);
			}
			newLoadMore.setCounterpart(this.counterpart);
		}
	}

	load() {
		var instance = this;
		$.ajax({url: "/api/events", data: {"time": this.time.getTime(), "before": !this.forward}, success: function(data) { instance.replace(data); }});
	}
}

var initializedTimeline = false;
function initializeTimeline(start, end) {
	initializedTimeline = true;
	loadMoreStart = new LoadMore(new Date(start), true);
	loadMoreEnd = new LoadMore(new Date(end), false);
	loadMoreStart.setCounterpart(loadMoreEnd);
}
