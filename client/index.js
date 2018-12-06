(function() {
    var App = document.querySelector('#app');
    var Store = function(state, reducers) {
        self = this;
        self.observers = [];
        self.state = state || {};
        self.dispatch = function() {
            self.state = reducers(state);
            self.notify();
        }
        self.notify = function () {
            for (var i = 0; i < self.observers.length; i++) {
                var observer = self.observers[i];
                observer.react(self.state);
            }
        }
        self.register = function(observer) {
            self.observers.push(observer);
        }
    }
    var reducers = function(action, state) {
        return function(action) {
            switch(action) {
                case "@search":
                    return;
            }
        }
    }
    var Component = function(el) {
        this.element = el;
        this.append = function(component) {
            this.element.appendChild(component.element);
        }
        this.react = function() {}
    };
    var Search = function(el) {
        Component.call(el);
        var self = this;
    };
    var Article = function(el) {
        Component.call(el);
        var self = this;
    };
    var ResultSide = function(el) {
        Component.call(el);
        var self = this;
    };
})();