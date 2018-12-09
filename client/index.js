(function() {
    function $ (selector, el) {
        if (el) {
            return el.querySelector(selector);
        }
        return document.querySelector(selector);
    }
    function $$ (selector, el) {
        if (el) {
            return el.querySelector(selector);
        }
        return document.querySelectorAll(selector);
    }

    var Api = {
        getArticles: (query) => {
            return fetch('/search?shops=gigantti,verkkokauppa&size=100&query=' + query).then(
                response => response.json().then(data => data)
            );
        }
    };

    var Store = function(state, reducers) {
        self = this;
        self.observers = [];
        self.state = state || {};
        self.dispatch = function(action) {
            self.state = reducers(action, self.state);
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
        switch(action.type) {
            case "@search/request":
                return Object.assign(
                    state,
                    { search: { query: action.query, results: undefined }, loading: true }
                );
            case "@search/done":
                return Object.assign(
                    state,
                    { search: { results: action.results }, loading: false }
                );
        }
        return state;
    }
    var store = new Store({}, reducers);

    function Component(el) {
        this.element = el;
    };
    Component.prototype.append = function(component) {
        this.element.appendChild(component.element);
    }
    Component.prototype.react = function(component) {}

    function SearchBar(el) {
        Component.call(this, el);
        var self = this;
        var input = $('input', el);
        var submitBtn = $('button', el);
        input.addEventListener("keyup", function(event) {
            event.preventDefault();
            if (event.keyCode === 13) {
                submitBtn.click();
            }
        });
        submitBtn.addEventListener("click", function(event) {
            var query = input.value;
            store.dispatch({ type: '@search/request', query: query });
            Api.getArticles(query).then(data => {
                store.dispatch({ type: '@search/done', results: data });
            }).catch(e => {
                console.error(e);
                store.dispatch({ type: '@search/done', results: response });
            })
        });
    };
    function SearchResult(sides = []) {
        var el = document.createElement('div');
        el.classList = 'comparison__results';
        Component.call(this, el);
        var self = this;
        self.template = $('template#comparison__result').content;
        self.sides = sides.map(side => {
            const resultSide = new SearchResultSide(
                self.template.cloneNode(true),
                side
            );

            Component.prototype.append.call(self, resultSide);
            return {
                key: side.key,
                el: resultSide
            }
        });

        self.update = function(data) {
            self.sides.forEach(side => {
                side.el.update(data[side.key]);
            });
        }
    };

    SearchResult.prototype.react = function(gState) {
        const state = gState.search;
        if (state && state.results) {
            this.update(state.results);
        }
    }

    function Article(el, data) {
        Component.call(this, el);
        var self = this;
        $('.comparison__article-image', el).src = data.image;
        $('.comparison__article-link', el).href = data.link;
        $('.comparison__article-link', el).textContent = data.name;
        $('.comparison__article-price', el).textContent = data.price + ' €';
    };

    function ArticleList(el) {
        Component.call(this, el);
        var self = this;
        self.article_template = $('template#comparison__article').content;
        self.clear = function () {
            while (self.element.firstChild) {
                self.element.removeChild(self.element.firstChild);
            }
        }
        self.update = function(articlesData) {
            self.clear();
            articlesData.forEach(article => {
                var el = new Article(self.article_template.cloneNode(true), article);
                Component.prototype.append.call(self, el);
            });
        }
    };

    function SearchResultSide(el, sideObj) {
        Component.call(this, el);
        var self = this;
        self.title = $('.comparison__result-title', el);
        self.count = $('.comparison__result-count', el);
        self.articles = new ArticleList($('.comparison__result-articles', el));
        self.update = function(data) {
            self.title.textContent = data.shop;
            self.count.textContent = data.count;
            if (data.items) {
                self.articles.update(data.items || []);
            }
        }
        self.update(sideObj);
    }

    function Loader(el) {
        Component.call(this, el);
    }

    Loader.prototype.react = function(state) {
        if (state.loading) {
            this.element.classList.remove('hidden');
        } else {
            this.element.classList.add('hidden');
        }
    }

    var App = new Component($('#app'));
    var LoaderEl = new Loader($('.loader-container'));
    var searchBar = new SearchBar(
        $('template#comparison__search').content.cloneNode(true)
    );

    var searchResult = new SearchResult([
        {
            key: 'verkkokauppa',
            shop: 'Verkkokauppa',
            count: 'No result'
        },
        {
            key: 'gigantti',
            shop: 'Gigantti',
            count: 'No result'
        }
    ]);

    App.append(searchBar);
    App.append(searchResult);

    store.register(LoaderEl);
    store.register(searchResult);
})();