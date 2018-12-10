(function() {
    function $ (selector, el) {
        if (el) {
            return el.querySelector(selector);
        }
        return document.querySelector(selector);
    }
    function $$ (selector, el) {
        if (el) {
            return el.querySelectorAll(selector);
        }
        return document.querySelectorAll(selector);
    }

    var Api = {
        getArticles: (query) =>
            fetch(
                '/search?shops=gigantti,verkkokauppa,jimms&size=100&query=' + query,
                {
                    method: "GET",
                    headers: {
                        "Authorization": new Date().getTime() / 1000
                    },
                }
            ).then(
                response => response.json().then(data => data)
            ),
        dogeSearch: (query) => 
            fetch(
                '/gsearch?query=' + query,
                {
                    method: "GET",
                    headers: {
                        "Authorization": new Date().getTime() / 1000
                    },
                }
            ).then(
                response => response.json()
                    .then(data => data.map(
                        e => Object.assign(
                            e._source,
                            { body: e._source.body.substr(0, 210) },
                            e.highlight
                        )
                    ))
            )
    };

    var Store = function(state, reducers) {
        var self = this;
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
            case "@doge/request":
                return Object.assign(
                    state,
                    { doge: { query: action.query, results: undefined }, loading: true }
                );
            case "@doge/done":
                return Object.assign(
                    state,
                    { doge: { results: action.results }, loading: false }
                );
            case "@switch":
                return Object.assign(
                    state,
                    { content: action.content }
                );
        }
        return state;
    }
    var store = new Store({
        content: 'comparison'
    }, reducers);

    function Component(el) {
        this.element = el;
    };
    Component.prototype.append = function(component) {
        this.element.appendChild(component.element);
    }
    Component.prototype.react = function(component) {}

    function SearchBar(el, options) {
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
        submitBtn.addEventListener("click", () => {
            var query = input.value;
            options.onClick(query);
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

    function Menu(el, options) {
        Component.call(this, el);
        var self = this;
        self.options = options.map(option => {
            var item = document.createElement('li');
            item.classList.add('navigation-item');
            item.textContent = option.value;
            item.dataset.key = option.key;
            if (option.selected) {
                item.classList.add('navigation-item--selected');
            }
            self.element.appendChild(item);
        });
        
        self.element.addEventListener("click", function(event) {
            var target = event.target;
            var selectedItem = target.closest('.navigation-item');
            if (selectedItem) {
                Array.from($$('.navigation-item', el)).forEach(
                    e => e.classList.remove('navigation-item--selected')
                )
                selectedItem.classList.add('navigation-item--selected');
                var key = selectedItem.dataset.key;
                store.dispatch({ type: '@switch', content: key })
            }
        });
    }

    function DogeTextResult(el, data) {
        Component.call(this, el);
        $('.doge__result-link', el).href = data.url;
        $('.doge__result-title', el).innerHTML = data.title;
        $('.doge__result-origin', el).textContent = data.url;
        $('.doge__result-body', el).innerHTML = data.body || '';
        $('.doge__result-tags', el).innerHTML = data.tags || '';
    };

    function DogeTextResultList() {
        var el = document.createElement('ul');
        el.classList.add('doge__results');
        Component.call(this, el);
        var self = this;
        self.article_template = $('template#doge__result').content;
        self.clear = function () {
            while (self.element.firstChild) {
                self.element.removeChild(self.element.firstChild);
            }
        }
        self.update = function(dogeData) {
            self.clear();
            dogeData.forEach(doge => {
                var el = new DogeTextResult(self.article_template.cloneNode(true), doge);
                Component.prototype.append.call(self, el);
            });
        }
    };

    DogeTextResultList.prototype.react = function(gState) {
        var state = gState.doge;
        if (state && state.results) {
            this.update(state.results);
        }
    }

    var LoaderEl = new Loader($('.loader-container'));
    var ComparisonSearchBar = new SearchBar(
        $('template#comparison__search').content.cloneNode(true),
        {
            onClick: function(query) {
                store.dispatch({ type: '@search/request', query: query });
                Api.getArticles(query).then(data => {
                    store.dispatch({ type: '@search/done', results: data });
                }).catch(e => {
                    console.error(e);
                    store.dispatch({ type: '@search/done', results: [] });
                })
            }
        }
    );
    var DogeSearchBar = new SearchBar(
        $('template#comparison__search').content.cloneNode(true),
        {
            onClick: function(query) {
                store.dispatch({ type: '@doge/request', query: query });
                Api.dogeSearch(query).then(data => {
                    store.dispatch({ type: '@doge/done', results: data });
                }).catch(e => {
                    console.error(e);
                    store.dispatch({ type: '@doge/done', results: [] });
                })
            }
        }
    );

    var ComparisonSearchResult = new SearchResult([
        {
            key: 'verkkokauppa',
            shop: 'Verkkokauppa',
            count: 'No result'
        },
        {
            key: 'gigantti',
            shop: 'Gigantti',
            count: 'No result'
        },
        {
            key: 'jimms',
            shop: "JIMM'S",
            count: 'No result'
        }
    ]);

    var App = new Component($('#app'));
    var Comparison = new Component($('#comparison'));
    var DogeSearch = new Component($('#doge-search'));
    App.react = function(state) {
        var pages = Array.from($$('#app #page > *'));
        pages.forEach(page => {
            if (page.id === state.content) {
                page.classList.remove('hidden');
            } else {
                page.classList.add('hidden');
            }
        });
    };

    var Menu = new Menu($('#navigation'), [
        {
            key: 'comparison',
            selected: true,
            value: 'Comparison'
        },
        {
            key: 'doge-search',
            selected: false,
            value: 'DSearch'
        }
    ]);

    var DogeResults = new DogeTextResultList();

    Comparison.append(ComparisonSearchBar);
    Comparison.append(ComparisonSearchResult);
    DogeSearch.append(DogeSearchBar);
    DogeSearch.append(DogeResults);
    store.register(App);
    store.register(LoaderEl);
    store.register(ComparisonSearchResult);
    store.register(DogeResults);
})();