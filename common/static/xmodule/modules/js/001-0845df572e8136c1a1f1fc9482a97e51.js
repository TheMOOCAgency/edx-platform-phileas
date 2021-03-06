// Generated by CoffeeScript 1.6.1
(function() {
  var _this = this;

  this.Sequence = (function() {

    function Sequence(element) {
      var _this = this;
      this.removeBookmarkIconFromActiveNavItem = function(event) {
        return Sequence.prototype.removeBookmarkIconFromActiveNavItem.apply(_this, arguments);
      };
      this.addBookmarkIconToActiveNavItem = function(event) {
        return Sequence.prototype.addBookmarkIconToActiveNavItem.apply(_this, arguments);
      };
      this._change_sequential = function(direction, event) {
        return Sequence.prototype._change_sequential.apply(_this, arguments);
      };
      this.selectPrevious = function(event) {
        return Sequence.prototype.selectPrevious.apply(_this, arguments);
      };
      this.selectNext = function(event) {
        return Sequence.prototype.selectNext.apply(_this, arguments);
      };
      this.goto = function(event) {
        return Sequence.prototype.goto.apply(_this, arguments);
      };
      this.toggleArrows = function() {
        return Sequence.prototype.toggleArrows.apply(_this, arguments);
      };
      this.updateProgress = function() {
        return Sequence.prototype.updateProgress.apply(_this, arguments);
      };
      this.addToUpdatedProblems = function(problem_id, new_content_state) {
        return Sequence.prototype.addToUpdatedProblems.apply(_this, arguments);
      };
      this.hideTabTooltip = function(event) {
        return Sequence.prototype.hideTabTooltip.apply(_this, arguments);
      };
      this.displayTabTooltip = function(event) {
        return Sequence.prototype.displayTabTooltip.apply(_this, arguments);
      };
      this.updatedProblems = {};
      this.requestToken = $(element).data('request-token');
      this.el = $(element).find('.sequence');
      this.contents = this.$('.seq_contents');
      this.content_container = this.$('#seq_content');
      this.sr_container = this.$('.sr-is-focusable');
      this.num_contents = this.contents.length;
      this.id = this.el.data('id');
      this.ajaxUrl = this.el.data('ajax-url');
      this.nextUrl = this.el.data('next-url');
      this.prevUrl = this.el.data('prev-url');
      this.base_page_title = " | " + document.title;
      this.initProgress();
      this.bind();
      this.render(parseInt(this.el.data('position')));
    }

    Sequence.prototype.$ = function(selector) {
      return $(selector, this.el);
    };

    Sequence.prototype.bind = function() {
      this.$('#sequence-list .nav-item').click(this.goto);
      this.el.on('bookmark:add', this.addBookmarkIconToActiveNavItem);
      this.el.on('bookmark:remove', this.removeBookmarkIconFromActiveNavItem);
      this.$('#sequence-list .nav-item').on('focus mouseenter', this.displayTabTooltip);
      return this.$('#sequence-list .nav-item').on('blur mouseleave', this.hideTabTooltip);
    };

    Sequence.prototype.displayTabTooltip = function(event) {
      return $(event.currentTarget).find('.sequence-tooltip').removeClass('sr');
    };

    Sequence.prototype.hideTabTooltip = function(event) {
      return $(event.currentTarget).find('.sequence-tooltip').addClass('sr');
    };

    Sequence.prototype.initProgress = function() {
      return this.progressTable = {};
    };

    Sequence.prototype.updatePageTitle = function() {
      var position_link;
      position_link = this.link_for(this.position);
      if (position_link && position_link.data('page-title')) {
        return document.title = position_link.data('page-title') + this.base_page_title;
      }
    };

    Sequence.prototype.hookUpContentStateChangeEvent = function() {
      var _this = this;
      return $('.problems-wrapper').bind('contentChanged', function(event, problem_id, new_content_state) {
        return _this.addToUpdatedProblems(problem_id, new_content_state);
      });
    };

    Sequence.prototype.addToUpdatedProblems = function(problem_id, new_content_state) {
      if (!this.anyUpdatedProblems(this.position)) {
        this.updatedProblems[this.position] = {};
      }
      return this.updatedProblems[this.position][problem_id] = new_content_state;
    };

    Sequence.prototype.anyUpdatedProblems = function(position) {
      return this.updatedProblems[position] !== void 0;
    };

    Sequence.prototype.hookUpProgressEvent = function() {
      return $('.problems-wrapper').bind('progressChanged', this.updateProgress);
    };

    Sequence.prototype.mergeProgress = function(p1, p2) {
      var w1, w2;
      if (p1 === "NA") {
        return p2;
      }
      if (p2 === "NA") {
        return p1;
      }
      if (p1 === "done" && p2 === "done") {
        return "done";
      }
      w1 = p1 === "done" || p1 === "in_progress";
      w2 = p2 === "done" || p2 === "in_progress";
      if (w1 || w2) {
        return "in_progress";
      }
      return "none";
    };

    Sequence.prototype.updateProgress = function() {
      var new_progress;
      new_progress = "NA";
      _this = this;
      $('.problems-wrapper').each(function(index) {
        var progress;
        progress = $(this).data('progress_status');
        return new_progress = _this.mergeProgress(progress, new_progress);
      });
      this.progressTable[this.position] = new_progress;
      return this.setProgress(new_progress, this.link_for(this.position));
    };

    Sequence.prototype.setProgress = function(progress, element) {
      element.removeClass('progress-none').removeClass('progress-some').removeClass('progress-done');
      switch (progress) {
        case 'none':
          return element.addClass('progress-none');
        case 'in_progress':
          return element.addClass('progress-some');
        case 'done':
          return element.addClass('progress-done');
      }
    };

    Sequence.prototype.enableButton = function(button_class, button_action) {
      return this.$(button_class).removeClass('disabled').removeAttr('disabled').click(button_action);
    };

    Sequence.prototype.disableButton = function(button_class) {
      return this.$(button_class).addClass('disabled').attr('disabled', true);
    };

    Sequence.prototype.setButtonLabel = function(button_class, button_label) {
      return this.$(button_class + ' .sr').html(button_label);
    };

    Sequence.prototype.updateButtonState = function(button_class, button_action, action_label_prefix, is_at_boundary, boundary_url) {
      var button_label;
      if (is_at_boundary && boundary_url === 'None') {
        return this.disableButton(button_class);
      } else {
        button_label = action_label_prefix + (is_at_boundary ? ' Subsection' : ' Unit');
        this.setButtonLabel(button_class, button_label);
        return this.enableButton(button_class, button_action);
      }
    };

    Sequence.prototype.toggleArrows = function() {
      var is_first_tab, is_last_tab, next_button_class, previous_button_class;
      this.$('.sequence-nav-button').unbind('click');
      is_first_tab = this.position === 1;
      previous_button_class = '.sequence-nav-button.button-previous';
      this.updateButtonState(previous_button_class, this.selectPrevious, 'Previous', is_first_tab, this.prevUrl);
      is_last_tab = this.position >= this.contents.length;
      next_button_class = '.sequence-nav-button.button-next';
      return this.updateButtonState(next_button_class, this.selectNext, 'Next', is_last_tab, this.nextUrl);
    };

    Sequence.prototype.render = function(new_position) {
      var bookmarked, current_tab, modx_full_url, sequence_links,
        _this = this;
      if (this.position !== new_position) {
        if (this.position !== void 0) {
          this.mark_visited(this.position);
          modx_full_url = "" + this.ajaxUrl + "/goto_position";
          $.postWithPrefix(modx_full_url, {
            position: new_position
          });
        }
        this.el.trigger("sequence:change");
        this.mark_active(new_position);
        current_tab = this.contents.eq(new_position - 1);
        bookmarked = this.el.find('.active .bookmark-icon').hasClass('bookmarked') ? true : false;
        this.content_container.html(current_tab.text()).attr("aria-labelledby", current_tab.attr("aria-labelledby")).data('bookmarked', bookmarked);
        if (this.anyUpdatedProblems(new_position)) {
          $.each(this.updatedProblems[new_position], function(problem_id, latest_content) {
            return _this.content_container.find("[data-problem-id='" + problem_id + "']").data('content', latest_content);
          });
        }
        XBlock.initializeBlocks(this.content_container, this.requestToken);
        window.update_schematics();
        this.position = new_position;
        this.toggleArrows();
        this.hookUpContentStateChangeEvent();
        this.hookUpProgressEvent();
        this.updatePageTitle();
        sequence_links = this.content_container.find('a.seqnav');
        sequence_links.click(this.goto);
        this.el.find('.path').text(this.el.find('.nav-item.active').data('path'));
        return this.sr_container.focus();
      }
    };

    Sequence.prototype.goto = function(event) {
      var alert_template, alert_text, is_bottom_nav, new_position, widget_placement;
      event.preventDefault();
      if ($(event.currentTarget).hasClass('seqnav')) {
        new_position = $(event.currentTarget).attr('href');
      } else {
        new_position = $(event.currentTarget).data('element');
      }
      if ((1 <= new_position) && (new_position <= this.num_contents)) {
        is_bottom_nav = $(event.target).closest('nav[class="sequence-bottom"]').length > 0;
        if (is_bottom_nav) {
          widget_placement = 'bottom';
        } else {
          widget_placement = 'top';
        }
        Logger.log("edx.ui.lms.sequence.tab_selected", {
          current_tab: this.position,
          target_tab: new_position,
          tab_count: this.num_contents,
          id: this.id,
          widget_placement: widget_placement
        });
        if (window.queuePollerID) {
          window.clearTimeout(window.queuePollerID);
          delete window.queuePollerID;
        }
        return this.render(new_position);
      } else {
        alert_template = gettext("Sequence error! Cannot navigate to %(tab_name)s in the current SequenceModule. Please contact the course staff.");
        alert_text = interpolate(alert_template, {
          tab_name: new_position
        }, true);
        return alert(alert_text);
      }
    };

    Sequence.prototype.selectNext = function(event) {
      return this._change_sequential('next', event);
    };

    Sequence.prototype.selectPrevious = function(event) {
      return this._change_sequential('previous', event);
    };

    Sequence.prototype._change_sequential = function(direction, event) {
      var analytics_event_name, is_bottom_nav, new_position, offset, widget_placement;
      if (direction !== 'previous' && direction !== 'next') {
        return;
      }
      event.preventDefault();
      analytics_event_name = "edx.ui.lms.sequence." + direction + "_selected";
      is_bottom_nav = $(event.target).closest('nav[class="sequence-bottom"]').length > 0;
      if (is_bottom_nav) {
        widget_placement = 'bottom';
      } else {
        widget_placement = 'top';
      }
      Logger.log(analytics_event_name, {
        id: this.id,
        current_tab: this.position,
        tab_count: this.num_contents,
        widget_placement: widget_placement
      });
      if ((direction === 'next') && (this.position >= this.contents.length)) {
        return window.location.href = this.nextUrl;
      } else if ((direction === 'previous') && (this.position === 1)) {
        return window.location.href = this.prevUrl;
      } else {
        if (is_bottom_nav) {
          $.scrollTo(0, 150);
        }
        offset = {
          next: 1,
          previous: -1
        };
        new_position = this.position + offset[direction];
        return this.render(new_position);
      }
    };

    Sequence.prototype.link_for = function(position) {
      return this.$("#sequence-list .nav-item[data-element=" + position + "]");
    };

    Sequence.prototype.mark_visited = function(position) {
      var element;
      element = this.link_for(position);
      return element.removeClass("inactive").removeClass("active").addClass("visited");
    };

    Sequence.prototype.mark_active = function(position) {
      var element;
      element = this.link_for(position);
      return element.removeClass("inactive").removeClass("visited").addClass("active");
    };

    Sequence.prototype.addBookmarkIconToActiveNavItem = function(event) {
      event.preventDefault();
      this.el.find('.nav-item.active .bookmark-icon').removeClass('is-hidden').addClass('bookmarked');
      return this.el.find('.nav-item.active .bookmark-icon-sr').text(gettext('Bookmarked'));
    };

    Sequence.prototype.removeBookmarkIconFromActiveNavItem = function(event) {
      event.preventDefault();
      this.el.find('.nav-item.active .bookmark-icon').removeClass('bookmarked').addClass('is-hidden');
      return this.el.find('.nav-item.active .bookmark-icon-sr').text('');
    };

    return Sequence;

  })();

}).call(this);
