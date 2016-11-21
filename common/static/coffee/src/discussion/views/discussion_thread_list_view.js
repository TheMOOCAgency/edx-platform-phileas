// Generated by CoffeeScript 1.6.1
(function() {
  var _this = this,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  if (typeof Backbone !== "undefined" && Backbone !== null) {
    this.DiscussionThreadListView = (function(_super) {
      var _this = this;

      __extends(DiscussionThreadListView, _super);

      function DiscussionThreadListView() {
        var _this = this;
        this.updateEmailNotifications = function() {
          return DiscussionThreadListView.prototype.updateEmailNotifications.apply(_this, arguments);
        };
        this.retrieveFollowed = function() {
          return DiscussionThreadListView.prototype.retrieveFollowed.apply(_this, arguments);
        };
        this.chooseCohort = function(event) {
          return DiscussionThreadListView.prototype.chooseCohort.apply(_this, arguments);
        };
        this.chooseFilter = function(event) {
          return DiscussionThreadListView.prototype.chooseFilter.apply(_this, arguments);
        };
        this.filterTopics = function(event) {
          return DiscussionThreadListView.prototype.filterTopics.apply(_this, arguments);
        };
        this.toggleBrowseMenu = function(event) {
          return DiscussionThreadListView.prototype.toggleBrowseMenu.apply(_this, arguments);
        };
        this.hideBrowseMenu = function() {
          return DiscussionThreadListView.prototype.hideBrowseMenu.apply(_this, arguments);
        };
        this.showBrowseMenu = function() {
          return DiscussionThreadListView.prototype.showBrowseMenu.apply(_this, arguments);
        };
        this.isBrowseMenuVisible = function() {
          return DiscussionThreadListView.prototype.isBrowseMenuVisible.apply(_this, arguments);
        };
        this.threadRemoved = function(thread_id) {
          return DiscussionThreadListView.prototype.threadRemoved.apply(_this, arguments);
        };
        this.threadSelected = function(e) {
          return DiscussionThreadListView.prototype.threadSelected.apply(_this, arguments);
        };
        this.renderThread = function(thread) {
          return DiscussionThreadListView.prototype.renderThread.apply(_this, arguments);
        };
        this.loadMorePages = function(event) {
          return DiscussionThreadListView.prototype.loadMorePages.apply(_this, arguments);
        };
        this.showMetadataAccordingToSort = function() {
          return DiscussionThreadListView.prototype.showMetadataAccordingToSort.apply(_this, arguments);
        };
        this.renderThreads = function() {
          return DiscussionThreadListView.prototype.renderThreads.apply(_this, arguments);
        };
        this.updateSidebar = function() {
          return DiscussionThreadListView.prototype.updateSidebar.apply(_this, arguments);
        };
        this.addAndSelectThread = function(thread) {
          return DiscussionThreadListView.prototype.addAndSelectThread.apply(_this, arguments);
        };
        this.reloadDisplayedCollection = function(thread) {
          return DiscussionThreadListView.prototype.reloadDisplayedCollection.apply(_this, arguments);
        };
        this.clearSearchAlerts = function() {
          return DiscussionThreadListView.prototype.clearSearchAlerts.apply(_this, arguments);
        };
        this.removeSearchAlert = function(searchAlert) {
          return DiscussionThreadListView.prototype.removeSearchAlert.apply(_this, arguments);
        };
        this.addSearchAlert = function(message) {
          return DiscussionThreadListView.prototype.addSearchAlert.apply(_this, arguments);
        };
        return DiscussionThreadListView.__super__.constructor.apply(this, arguments);
      }

      DiscussionThreadListView.prototype.events = {
        "click .forum-nav-browse": "toggleBrowseMenu",
        "keypress .forum-nav-browse-filter-input": function(event) {
          return DiscussionUtil.ignoreEnterKey(event);
        },
        "keyup .forum-nav-browse-filter-input": "filterTopics",
        "click .forum-nav-browse-menu-wrapper": "ignoreClick",
        "click .forum-nav-browse-title": "selectTopicHandler",
        "keydown .forum-nav-search-input": "performSearch",
        "click .fa-search": "performSearch",
        "change .forum-nav-sort-control": "sortThreads",
        "click .forum-nav-thread-link": "threadSelected",
        "click .forum-nav-load-more-link": "loadMorePages",
        "change .forum-nav-filter-main-control": "chooseFilter",
        "change .forum-nav-filter-cohort-control": "chooseCohort"
      };

      DiscussionThreadListView.prototype.initialize = function(options) {
        var _this = this;
        this.courseSettings = options.courseSettings;
        this.displayedCollection = new Discussion(this.collection.models, {
          pages: this.collection.pages
        });
        this.collection.on("change", this.reloadDisplayedCollection);
        this.discussionIds = "";
        this.collection.on("reset", function(discussion) {
          var board;
          board = $(".current-board").html();
          _this.displayedCollection.current_page = discussion.current_page;
          _this.displayedCollection.pages = discussion.pages;
          return _this.displayedCollection.reset(discussion.models);
        });
        this.collection.on("add", this.addAndSelectThread);
        this.sidebar_padding = 10;
        this.boardName;
        this.template = _.template($("#thread-list-template").html());
        this.current_search = "";
        this.mode = 'all';
        this.searchAlertCollection = new Backbone.Collection([], {
          model: Backbone.Model
        });
        this.searchAlertCollection.on("add", function(searchAlert) {
          var content;
          content = _.template($("#search-alert-template").html())({
            'message': searchAlert.attributes.message,
            'cid': searchAlert.cid
          });
          _this.$(".search-alerts").append(content);
          return _this.$("#search-alert-" + searchAlert.cid + " a.dismiss").bind("click", searchAlert, function(event) {
            return _this.removeSearchAlert(event.data.cid);
          });
        });
        this.searchAlertCollection.on("remove", function(searchAlert) {
          return _this.$("#search-alert-" + searchAlert.cid).remove();
        });
        return this.searchAlertCollection.on("reset", function() {
          return _this.$(".search-alerts").empty();
        });
      };

      DiscussionThreadListView.prototype.addSearchAlert = function(message) {
        var m;
        m = new Backbone.Model({
          "message": message
        });
        this.searchAlertCollection.add(m);
        return m;
      };

      DiscussionThreadListView.prototype.removeSearchAlert = function(searchAlert) {
        return this.searchAlertCollection.remove(searchAlert);
      };

      DiscussionThreadListView.prototype.clearSearchAlerts = function() {
        return this.searchAlertCollection.reset();
      };

      DiscussionThreadListView.prototype.reloadDisplayedCollection = function(thread) {
        var active, content, current_el, thread_id;
        this.clearSearchAlerts();
        thread_id = thread.get('id');
        content = this.renderThread(thread);
        current_el = this.$(".forum-nav-thread[data-id=" + thread_id + "]");
        active = current_el.has(".forum-nav-thread-link.is-active").length !== 0;
        current_el.replaceWith(content);
        this.showMetadataAccordingToSort();
        if (active) {
          return this.setActiveThread(thread_id);
        }
      };

      DiscussionThreadListView.prototype.addAndSelectThread = function(thread) {
        var commentable_id, menuItem,
          _this = this;
        commentable_id = thread.get("commentable_id");
        menuItem = this.$(".forum-nav-browse-menu-item[data-discussion-id]").filter(function() {
          return $(this).data("discussion-id") === commentable_id;
        });
        this.setCurrentTopicDisplay(this.getPathText(menuItem));
        return this.retrieveDiscussion(commentable_id, function() {
          return _this.trigger("thread:created", thread.get('id'));
        });
      };

      DiscussionThreadListView.prototype.updateSidebar = function() {
        var amount, browseFilterHeight, discussionBody, discussionBottomOffset, discussionsBodyBottom, discussionsBodyTop, headerHeight, refineBarHeight, scrollTop, sidebar, sidebarHeight, topOffset, windowHeight;
        scrollTop = $(window).scrollTop();
        windowHeight = $(window).height();
        discussionBody = $(".discussion-column");
        discussionsBodyTop = discussionBody[0] ? discussionBody.offset().top : void 0;
        discussionsBodyBottom = discussionsBodyTop + discussionBody.outerHeight();
        sidebar = $(".forum-nav");
        if (scrollTop > discussionsBodyTop - this.sidebar_padding) {
          sidebar.css('top', scrollTop - discussionsBodyTop + this.sidebar_padding);
        } else {
          sidebar.css('top', '0');
        }
        sidebarHeight = windowHeight - Math.max(discussionsBodyTop - scrollTop, this.sidebar_padding);
        topOffset = scrollTop + windowHeight;
        discussionBottomOffset = discussionsBodyBottom + this.sidebar_padding;
        amount = Math.max(topOffset - discussionBottomOffset, 0);
        sidebarHeight = sidebarHeight - this.sidebar_padding - amount;
        sidebarHeight = Math.min(sidebarHeight + 1, discussionBody.outerHeight());
        sidebar.css('height', sidebarHeight);
        headerHeight = this.$(".forum-nav-header").outerHeight();
        refineBarHeight = this.$(".forum-nav-refine-bar").outerHeight();
        browseFilterHeight = this.$(".forum-nav-browse-filter").outerHeight();
        this.$('.forum-nav-thread-list').css('height', (sidebarHeight - headerHeight - refineBarHeight - 2) + 'px');
        return this.$('.forum-nav-browse-menu').css('height', (sidebarHeight - headerHeight - browseFilterHeight - 2) + 'px');
      };

      DiscussionThreadListView.prototype.ignoreClick = function(event) {
        return event.stopPropagation();
      };

      DiscussionThreadListView.prototype.render = function() {
        var _this = this;
        this.timer = 0;
        this.$el.html(this.template({
          isCohorted: this.courseSettings.get("is_cohorted"),
          isPrivilegedUser: DiscussionUtil.isPrivilegedUser()
        }));
        this.$(".forum-nav-sort-control option").removeProp("selected");
        this.$(".forum-nav-sort-control option[value=" + this.collection.sort_preference + "]").prop("selected", true);
        $(window).bind("load scroll resize", this.updateSidebar);
        this.displayedCollection.on("reset", this.renderThreads);
        this.displayedCollection.on("thread:remove", this.renderThreads);
        this.displayedCollection.on("change:commentable_id", function(model, commentable_id) {
          if (_this.mode === "commentables") {
            return _this.retrieveDiscussions(_this.discussionIds.split(","));
          }
        });
        this.renderThreads();
        return this;
      };

      DiscussionThreadListView.prototype.renderThreads = function() {
        var content, rendered, thread, _i, _len, _ref;
        this.$(".forum-nav-thread-list").html("");
        rendered = $("<div></div>");
        _ref = this.displayedCollection.models;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          thread = _ref[_i];
          content = this.renderThread(thread);
          rendered.append(content);
        }
        this.$(".forum-nav-thread-list").html(rendered.html());
        this.showMetadataAccordingToSort();
        this.renderMorePages();
        this.updateSidebar();
        return this.trigger("threads:rendered");
      };

      DiscussionThreadListView.prototype.showMetadataAccordingToSort = function() {
        var commentCounts, voteCounts;
        voteCounts = this.$(".forum-nav-thread-votes-count");
        commentCounts = this.$(".forum-nav-thread-comments-count");
        voteCounts.hide();
        commentCounts.hide();
        switch (this.$(".forum-nav-sort-control").val()) {
          case "activity":
          case "comments":
            return commentCounts.show();
          case "votes":
            return voteCounts.show();
        }
      };

      DiscussionThreadListView.prototype.renderMorePages = function() {
        if (this.displayedCollection.hasMorePages()) {
          return this.$(".forum-nav-thread-list").append("<li class='forum-nav-load-more'><a href='#' class='forum-nav-load-more-link'>" + gettext("Load more") + "</a></li>");
        }
      };

      DiscussionThreadListView.prototype.getLoadingContent = function(srText) {
        return '<div class="forum-nav-loading" tabindex="0"><span class="icon fa fa-spinner fa-spin"/><span class="sr" role="alert">' + srText + '</span></div>';
      };

      DiscussionThreadListView.prototype.loadMorePages = function(event) {
        var error, lastThread, loadMoreElem, loadingElem, options, _ref,
          _this = this;
        if (event) {
          event.preventDefault();
        }
        loadMoreElem = this.$(".forum-nav-load-more");
        loadMoreElem.html(this.getLoadingContent(gettext("Loading more threads")));
        loadingElem = loadMoreElem.find(".forum-nav-loading");
        DiscussionUtil.makeFocusTrap(loadingElem);
        loadingElem.focus();
        options = {
          filter: this.filter
        };
        switch (this.mode) {
          case 'search':
            options.search_text = this.current_search;
            if (this.group_id) {
              options.group_id = this.group_id;
            }
            break;
          case 'followed':
            options.user_id = window.user.id;
            break;
          case 'commentables':
            options.commentable_ids = this.discussionIds;
            if (this.group_id) {
              options.group_id = this.group_id;
            }
            break;
          case 'all':
            if (this.group_id) {
              options.group_id = this.group_id;
            }
        }
        lastThread = (_ref = this.collection.last()) != null ? _ref.get('id') : void 0;
        if (lastThread) {
          this.once("threads:rendered", function() {
            return $(".forum-nav-thread[data-id='" + lastThread + "'] + .forum-nav-thread .forum-nav-thread-link").focus();
          });
        } else {
          this.once("threads:rendered", function() {
            var _ref1;
            return (_ref1 = $(".forum-nav-thread-link").first()) != null ? _ref1.focus() : void 0;
          });
        }
        error = function() {
          _this.renderThreads();
          return DiscussionUtil.discussionAlert(gettext("Sorry"), gettext("We had some trouble loading more threads. Please try again."));
        };
        return this.collection.retrieveAnotherPage(this.mode, options, {
          sort_key: this.$(".forum-nav-sort-control").val()
        }, error);
      };

      DiscussionThreadListView.prototype.renderThread = function(thread) {
        var content, unreadCount;
        content = $(_.template($("#thread-list-item-template").html())(thread.toJSON()));
        unreadCount = thread.get('unread_comments_count') + (thread.get("read") ? 0 : 1);
        if (unreadCount > 0) {
          content.find('.forum-nav-thread-comments-count').attr("data-tooltip", interpolate(ngettext('%(unread_count)s new comment', '%(unread_count)s new comments', unreadCount), {
            unread_count: unreadCount
          }, true));
        }
        return content;
      };

      DiscussionThreadListView.prototype.threadSelected = function(e) {
        var thread_id;
        thread_id = $(e.target).closest(".forum-nav-thread").attr("data-id");
        this.setActiveThread(thread_id);
        this.trigger("thread:selected", thread_id);
        return false;
      };

      DiscussionThreadListView.prototype.threadRemoved = function(thread_id) {
        return this.trigger("thread:removed", thread_id);
      };

      DiscussionThreadListView.prototype.setActiveThread = function(thread_id) {
        this.$(".forum-nav-thread-link").find(".sr").remove();
        this.$(".forum-nav-thread[data-id!='" + thread_id + "'] .forum-nav-thread-link").removeClass("is-active");
        return this.$(".forum-nav-thread[data-id='" + thread_id + "'] .forum-nav-thread-link").addClass("is-active").find(".forum-nav-thread-wrapper-1").prepend('<span class="sr">' + gettext("Current conversation") + '</span>');
      };

      DiscussionThreadListView.prototype.goHome = function() {
        var thread_id, url,
          _this = this;
        this.template = _.template($("#discussion-home-template").html());
        $(".forum-content").html(this.template);
        $(".forum-nav-thread-list a").removeClass("is-active").find(".sr").remove();
        $("input.email-setting").bind("click", this.updateEmailNotifications);
        url = DiscussionUtil.urlFor("notifications_status", window.user.get("id"));
        DiscussionUtil.safeAjax({
          url: url,
          type: "GET",
          success: function(response, textStatus) {
            if (response.status) {
              return $('input.email-setting').attr('checked', 'checked');
            } else {
              return $('input.email-setting').removeAttr('checked');
            }
          }
        });
        thread_id = null;
        return this.trigger("thread:removed");
      };

      DiscussionThreadListView.prototype.isBrowseMenuVisible = function() {
        return this.$(".forum-nav-browse-menu-wrapper").is(":visible");
      };

      DiscussionThreadListView.prototype.showBrowseMenu = function() {
        if (!this.isBrowseMenuVisible()) {
          this.$(".forum-nav-browse").addClass("is-active");
          this.$(".forum-nav-browse-menu-wrapper").show();
          this.$(".forum-nav-thread-list-wrapper").hide();
          $(".forum-nav-browse-filter-input").focus();
          $("body").bind("click", this.hideBrowseMenu);
          return this.updateSidebar();
        }
      };

      DiscussionThreadListView.prototype.hideBrowseMenu = function() {
        if (this.isBrowseMenuVisible()) {
          this.$(".forum-nav-browse").removeClass("is-active");
          this.$(".forum-nav-browse-menu-wrapper").hide();
          this.$(".forum-nav-thread-list-wrapper").show();
          $("body").unbind("click", this.hideBrowseMenu);
          return this.updateSidebar();
        }
      };

      DiscussionThreadListView.prototype.toggleBrowseMenu = function(event) {
        event.preventDefault();
        event.stopPropagation();
        if (this.isBrowseMenuVisible()) {
          return this.hideBrowseMenu();
        } else {
          return this.showBrowseMenu();
        }
      };

      DiscussionThreadListView.prototype.getPathText = function(item) {
        var path, pathText, pathTitles;
        path = item.parents(".forum-nav-browse-menu-item").andSelf();
        pathTitles = path.children(".forum-nav-browse-title").map(function(i, elem) {
          return $(elem).text();
        }).get();
        return pathText = pathTitles.join(" / ");
      };

      DiscussionThreadListView.prototype.filterTopics = function(event) {
        var items, query,
          _this = this;
        query = $(event.target).val();
        items = this.$(".forum-nav-browse-menu-item");
        if (query.length === 0) {
          return items.show();
        } else {
          items.hide();
          return items.each(function(i, item) {
            var path, pathText;
            item = $(item);
            if (!item.is(":visible")) {
              pathText = _this.getPathText(item).toLowerCase();
              if (query.split(" ").every(function(term) {
                return pathText.search(term.toLowerCase()) !== -1;
              })) {
                path = item.parents(".forum-nav-browse-menu-item").andSelf();
                return path.add(item.find(".forum-nav-browse-menu-item")).show();
              }
            }
          });
        }
      };

      DiscussionThreadListView.prototype.setCurrentTopicDisplay = function(text) {
        return this.$(".forum-nav-browse-current").text(this.fitName(text));
      };

      DiscussionThreadListView.prototype.getNameWidth = function(name) {
        var test, width;
        test = $("<div>");
        test.css({
          "font-size": this.$(".forum-nav-browse-current").css('font-size'),
          opacity: 0,
          position: 'absolute',
          left: -1000,
          top: -1000
        });
        $("body").append(test);
        test.html(name);
        width = test.width();
        test.remove();
        return width;
      };

      DiscussionThreadListView.prototype.fitName = function(name) {
        var partialName, path, prefix, rawName, width, x;
        this.maxNameWidth = this.$(".forum-nav-browse").width() - this.$(".forum-nav-browse .icon").outerWidth(true) - this.$(".forum-nav-browse-drop-arrow").outerWidth(true);
        width = this.getNameWidth(name);
        if (width < this.maxNameWidth) {
          return name;
        }
        path = (function() {
          var _i, _len, _ref, _results;
          _ref = name.split("/");
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            x = _ref[_i];
            _results.push(x.replace(/^\s+|\s+$/g, ""));
          }
          return _results;
        })();
        prefix = "";
        while (path.length > 1) {
          prefix = gettext("…") + "/";
          path.shift();
          partialName = prefix + path.join("/");
          if (this.getNameWidth(partialName) < this.maxNameWidth) {
            return partialName;
          }
        }
        rawName = path[0];
        name = prefix + rawName;
        while (this.getNameWidth(name) > this.maxNameWidth) {
          rawName = rawName.slice(0, rawName.length - 1);
          name = prefix + rawName + gettext("…");
        }
        return name;
      };

      DiscussionThreadListView.prototype.selectTopicHandler = function(event) {
        event.preventDefault();
        return this.selectTopic($(event.target));
      };

      DiscussionThreadListView.prototype.selectTopic = function($target) {
        var allItems, discussionIds, item;
        this.hideBrowseMenu();
        this.clearSearch();
        item = $target.closest('.forum-nav-browse-menu-item');
        this.setCurrentTopicDisplay(this.getPathText(item));
        if (item.hasClass("forum-nav-browse-menu-all")) {
          this.discussionIds = "";
          this.$('.forum-nav-filter-cohort').show();
          return this.retrieveAllThreads();
        } else if (item.hasClass("forum-nav-browse-menu-following")) {
          this.retrieveFollowed();
          return this.$('.forum-nav-filter-cohort').hide();
        } else {
          allItems = item.find(".forum-nav-browse-menu-item").andSelf();
          discussionIds = allItems.filter("[data-discussion-id]").map(function(i, elem) {
            return $(elem).data("discussion-id");
          }).get();
          this.retrieveDiscussions(discussionIds);
          return this.$(".forum-nav-filter-cohort").toggle(item.data('cohorted') === true);
        }
      };

      DiscussionThreadListView.prototype.chooseFilter = function(event) {
        this.filter = $(".forum-nav-filter-main-control :selected").val();
        return this.retrieveFirstPage();
      };

      DiscussionThreadListView.prototype.chooseCohort = function(event) {
        this.group_id = this.$('.forum-nav-filter-cohort-control :selected').val();
        return this.retrieveFirstPage();
      };

      DiscussionThreadListView.prototype.retrieveDiscussion = function(discussion_id, callback) {
        var url,
          _this = this;
        if (callback == null) {
          callback = null;
        }
        url = DiscussionUtil.urlFor("retrieve_discussion", discussion_id);
        return DiscussionUtil.safeAjax({
          url: url,
          type: "GET",
          success: function(response, textStatus) {
            _this.collection.current_page = response.page;
            _this.collection.pages = response.num_pages;
            _this.collection.reset(response.discussion_data);
            Content.loadContentInfos(response.annotated_content_info);
            _this.displayedCollection.reset(_this.collection.models);
            if (callback != null) {
              return callback();
            }
          }
        });
      };

      DiscussionThreadListView.prototype.retrieveDiscussions = function(discussion_ids) {
        this.discussionIds = discussion_ids.join(',');
        this.mode = 'commentables';
        return this.retrieveFirstPage();
      };

      DiscussionThreadListView.prototype.retrieveAllThreads = function() {
        this.mode = 'all';
        return this.retrieveFirstPage();
      };

      DiscussionThreadListView.prototype.retrieveFirstPage = function(event) {
        this.collection.current_page = 0;
        this.collection.reset();
        return this.loadMorePages(event);
      };

      DiscussionThreadListView.prototype.sortThreads = function(event) {
        this.displayedCollection.setSortComparator(this.$(".forum-nav-sort-control").val());
        return this.retrieveFirstPage(event);
      };

      DiscussionThreadListView.prototype.performSearch = function(event) {
        var text;
        if (event.which === 13 || event.type === 'click') {
          event.preventDefault();
          this.hideBrowseMenu();
          this.setCurrentTopicDisplay(gettext("Search Results"));
          text = this.$(".forum-nav-search-input").val();
          return this.searchFor(text);
        }
      };

      DiscussionThreadListView.prototype.searchFor = function(text) {
        var url,
          _this = this;
        this.clearSearchAlerts();
        this.clearFilters();
        this.mode = 'search';
        this.current_search = text;
        url = DiscussionUtil.urlFor("search");
        return DiscussionUtil.safeAjax({
          $elem: this.$(".forum-nav-search-input"),
          data: {
            text: text
          },
          url: url,
          type: "GET",
          dataType: 'json',
          $loading: $,
          loadingCallback: function() {
            return _this.$(".forum-nav-thread-list").html("<li class='forum-nav-load-more'>" + _this.getLoadingContent(gettext("Loading thread list")) + "</li>");
          },
          loadedCallback: function() {
            return _this.$(".forum-nav-thread-list .forum-nav-load-more").remove();
          },
          success: function(response, textStatus) {
            var message;
            if (textStatus === 'success') {
              _this.collection.reset(response.discussion_data);
              Content.loadContentInfos(response.annotated_content_info);
              _this.collection.current_page = response.page;
              _this.collection.pages = response.num_pages;
              if (!_.isNull(response.corrected_text)) {
                message = interpolate(_.escape(gettext('No results found for %(original_query)s. Showing results for %(suggested_query)s.')), {
                  "original_query": "<em>" + _.escape(text) + "</em>",
                  "suggested_query": "<em>" + response.corrected_text + "</em>"
                }, true);
                _this.addSearchAlert(message);
              } else if (response.discussion_data.length === 0) {
                _this.addSearchAlert(gettext('No threads matched your query.'));
              }
              _this.displayedCollection.reset(_this.collection.models);
              if (text) {
                return _this.searchForUser(text);
              }
            }
          }
        });
      };

      DiscussionThreadListView.prototype.searchForUser = function(text) {
        var _this = this;
        return DiscussionUtil.safeAjax({
          data: {
            username: text
          },
          url: DiscussionUtil.urlFor("users"),
          type: "GET",
          dataType: 'json',
          error: function() {},
          success: function(response) {
            var message;
            if (response.users.length > 0) {
              message = interpolate(_.escape(gettext('Show posts by %(username)s.')), {
                "username": _.template('<a class="link-jump" href="<%= url %>"><%- username %></a>')({
                  url: DiscussionUtil.urlFor("user_profile", response.users[0].id),
                  username: response.users[0].username
                })
              }, true);
              return _this.addSearchAlert(message);
            }
          }
        });
      };

      DiscussionThreadListView.prototype.clearSearch = function() {
        this.$(".forum-nav-search-input").val("");
        this.current_search = "";
        return this.clearSearchAlerts();
      };

      DiscussionThreadListView.prototype.clearFilters = function() {
        this.$(".forum-nav-filter-main-control").val("all");
        return this.$(".forum-nav-filter-cohort-control").val("all");
      };

      DiscussionThreadListView.prototype.retrieveFollowed = function() {
        this.mode = 'followed';
        return this.retrieveFirstPage();
      };

      DiscussionThreadListView.prototype.updateEmailNotifications = function() {
        var _this = this;
        if ($('input.email-setting').attr('checked')) {
          return DiscussionUtil.safeAjax({
            url: DiscussionUtil.urlFor("enable_notifications"),
            type: "POST",
            error: function() {
              return $('input.email-setting').removeAttr('checked');
            }
          });
        } else {
          return DiscussionUtil.safeAjax({
            url: DiscussionUtil.urlFor("disable_notifications"),
            type: "POST",
            error: function() {
              return $('input.email-setting').attr('checked', 'checked');
            }
          });
        }
      };

      return DiscussionThreadListView;

    }).call(this, Backbone.View);
  }

}).call(this);
