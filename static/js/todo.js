
var Todo = Backbone.Model.extend({
//    events:{
//      'sync':TodoSync
//    },
    defaults: function() {
        return {
            subject: "empty todo...",
            done: 0
        };
    },
    url:function(){
        return '/api/todo/'+this.id
    },
    toggle:function(){
        var done = (!this.get('done'))?1:0;
        this.save({done:done});
    },
    initialize: function() {
        if (!this.get("subject")) {
            this.set({"subject": this.defaults().subject});
        }
        if (!this.get("done")) {
            this.set({"done": this.defaults().done});
        }
        this.on('sync', this.afterSync);
        this.on('error', this.afterSync);
    },
    setDueDate:function(date){
        this.save({due_date:date});
    },
    preLink:function(todo_id){
        $.ajax({
            method:'post',
            url:'/api/todo/link/'+todo_id+'/'+this.id+'/',
            success:function(data){
                $.pnotify({
                    text: data,
                    type: 'info',
                    styling: 'bootstrap',
                    delay:2000,
                    history: false,
                    stack: false
                });
            }
        });
    },
    afterSync:function(model, resp, options){
        if(resp.model){
            this.set(resp.model);
        }
        if(resp && resp.message){
            $.pnotify({
                text: resp.message,
                type: resp.code==0?'info':'error',
                styling: 'bootstrap',
                delay:2000,
                history: false,
                stack: false
            });
        } else {
            $.pnotify({
                title:'骚瑞',
                text: '您刚刚的请求没有操作成功啊亲，重新来过吧',
                type: 'error',
                styling: 'bootstrap',
                delay:2000,
                history: false,
                stack: false
            });
        }

    }
});


var TodoView = Backbone.View.extend({
    id:function(){
        return 'todo-'+this.model.id;
    },
    isSingle:false,
    tagName:'li',
    className:function(){
        return 'todo '+(this.model.get('done')?'completed':'uncompleted');
    },
    initialize: function() {
        this.listenTo(this.model, "initialize", this.render);
        this.listenTo(this.model, "change", this.render);
    },
    events: {
        "click .todo-checkbox"   : "toggleDone",
        "click .todo-assignee": "assignUser"
    },
    template: function(){
        return $('#todo-template').html();
    },
    render:function(){
        var html = Mustache.render(this.template(), this.model.toJSON());
        this.$el.html(html);
        var self = this;
        this.$el.find('.link').data('todo_id', this.model.id);
        this.$el.find('.due-date').datepicker({
            format: 'yyyy-mm-dd',
            language:'zh-CN',
            autoclose:true
        }).on('changeDate', function(ev){
            var date = self.$el.find('.due-date').data('date');
            self.setDueDate(date);
        });
        if(this.model.get('due_date')){
            var model_due_date = this.model.get('due_date');
            var $due_date = this.$el.find('.due-date');
            $due_date.text(model_due_date);
            var today = new Date();
            var due_date = new Date(model_due_date);
            if(due_date<=today && !this.model.get('done')) {
                $due_date.addClass('badge-warning');
            }else{
                $due_date.removeClass('badge-warning');
            }
        }
        var assignee = this.model.get('assignee');
        if(assignee){
            this.$el.find('.todo-assignee').text(assignee.name).addClass('badge-info');
        } else {
            this.$el.find('.todo-assignee').text('未指派').removeClass('badge-info');
        }
        this.$el.find('.link').draggable({
            //cancel: "a.ui-icon", // clicking an icon won't initiate dragging
            revert: "invalid", // when not dropped, the item will revert back to its initial position
            containment: "document",
            helper: "clone",
            cursor: "move",
            zIndex: 100
        }).droppable({
            accept: ".todo .link",
            hoverClass: 'btn-info',
            drop: function( event, ui ) {
                self.model.preLink(ui.draggable.data('todo_id'));
            },
            activate: function( event, ui ) {
                $(this).addClass('btn-primary');

            },
            deactivate:function( event, ui ) {
                $(this).removeClass('btn-primary');
            }
        }).popover();

        return this;
    },
    toggleDone: function() {
        this.model.toggle();
        this.$el.toggleClass('completed').toggleClass('uncompleted');
        if(!this.isSingle){
            var $todolist = this.$el.parents('.todolist');
            var $comleted = $todolist.find('.todos-completed');
            var $uncompleted = $todolist.find('.todos-uncompleted');
            var self = this;
            if(this.$el.is('.completed')){
                this.$el.fadeOut(function(){
                    self.$el.prependTo($comleted).show();
                });
            } else {
                this.$el.fadeOut(function(){
                    self.$el.prependTo($uncompleted).show();
                });
            }
        }
    },
    setDueDate: function(date){
        this.$el.find('.due-date').datepicker('hide').off('changeDate');
        this.$el.find('.due-date').data('date', date);
        this.model.setDueDate(date);
    },
    assignUser:function(){
        var self = this;
        $('#myModal').modal().on('hidden', function(){
            var confirmed = $(this).data('confirm');
            if(confirmed){
                var assignee_uid = $('#assignee').val();
                self.model.save({assignee_uid:assignee_uid});
            }
            $(this).data('confirm', null);
            $(this).off('shown').off('hidden');
        }).on('shown', function(){
            var assignee_uid = 0;
            if(self.model.get('assignee')){
                assignee_uid = self.model.get('assignee').id;
            }
            $('#assignee').val(assignee_uid);
        });
    }
});

var _TodoList = Backbone.Collection.extend({
    model: Todo,
    initialize:function(){
    }
});

var List = Backbone.Model.extend({
    // Default attributes for the todo item.
    defaults: function() {
        return {
            name: "empty list",
            project_id: 0,
            todo_count:0,
            finish_count:0,
            has_finished:0,
            todo_status:G.todo_status?G.todo_status:1,
            show_list_title:true
        };
    },
    initialize: function() {
        if (!this.get("name")) {
            this.set({"name": this.defaults().name});
        }
        if (!this.get('todo_status')){
            this.set({"todo_status": this.defaults().todo_status});
        }
        if (typeof(G.show_list_title) != 'undefined') {
            this.set({"show_list_title":G.show_list_title});
        }
        var _list = new _TodoList;
        var _self = this;
        _list.on('reset', function(){
            _.map(_list.models, function(model){
                var _todo = new TodoView({model:model});
                _todo.render();
                if(!model.get('done')){
                    $('#todos-'+_self.id).append(_todo.$el);
                } else{
                    $('#todos-'+_self.id+'-completed').append(_todo.$el);
                }

            })
        });
        _list.url = '/api/lists/'+this.id+'/todos.json?_rnd='+Math.random();
        if(G.todo_status) {
            _list.url += '&done='+ G.todo_status
        }
        _list.fetch();

        this.todolist = _list;
    }
});
var TodoList = Backbone.Collection.extend({
    model: List,
    url: function(){
        return '/api/project/'+ G.project_id + '/lists.json';
    }
});


var TodoListView = Backbone.View.extend({
    className:'todolist',
    initialize: function() {
        this.listenTo(this.model, "change", this.render);
        this.listenTo(this.model.todolist, 'add', this.addOne);
        //console.log(this.model.todolist.model);
        //this.listenTo(this.model.todolist.model, "change", this.clickDone);
    },
    template: function(){
        return $('#todolist-template').html();
    },
    events:{
        'keypress .todo-content':'createOnEnter',
        'click .btn-create-todo':'createOnClick'
    },
    clickDone:function(){
        //console.log('done');
    },
    render:function(){
        var model = this.model.toJSON();
        model.team_users = G.team_users;
        var html = Mustache.render(this.template(), model);
        this.$el.html(html);
        this.$el.data('todolist_id', this.model.id);
        this.input = this.$el.find('.todo-content');
        this.bindNewTodoEvent();
        var self = this;
        this.$el.find('.todo-form .link-todo-due').datepicker({
            format: 'yyyy-mm-dd',
            language:'zh-CN',
            autoclose:true
        }).on('changeDate', function(ev){
            var date = self.$el.find('.todo-form .new-todo-due-date').val();
            var date_text = date;
            if(date == '0000-00-00') {
                date_text = '没有截止时间';
            }
            self.$el.find('.todo-form .due.add-on').text(date_text)
        });
        this.$el.find('.todos.todos-uncompleted').sortable({
            stop: function( event, ui ) {
                var $li = $(ui.item);
                var index = $li.index();
                var list_id = $li.parents('.todolist').data('todolist_id');
                var todo_id = $li.find('input').data('todo-id');
                $.ajax({
                    method:'post',
                    url:'/api/todo/move/'+todo_id+'/',
                    data:{
                        todolist_id:list_id,
                        index:index
                    },
                    success:function(text){
                        $.pnotify({
                            text: text,
                            type: 'info',
                            styling: 'bootstrap',
                            delay:2000,
                            history: false,
                            stack: false
                        });
                    }
                });
            },
            connectWith: ".todos.todos-uncompleted",
            revert: true

        });
        this.$el.find('.todos, .todos li').disableSelection();
        return this;
    },
    addOne: function(todo) {
        var view = new TodoView({model: todo});
        this.$("#todos-"+this.model.id).append(view.render().el);
    },
    createOnEnter:function(e){
        if (e.keyCode != 13) return;
        this.createOnClick();
        return false;
    },
    createOnClick:function(){
        if (!this.input.val()) return;
        var self = this;
        var assignee_uid = this.$el.find('select.todo-assignee option:selected').val();
        this.model.todolist.create(
            {
                subject: this.input.val(),
                due_date:this.$el.find('.new-todo-due-date').val(),
                assignee_uid:assignee_uid,
                point:this.$el.find('.new-todo-point').val()
            },
            {
                url: '/api/lists/'+self.model.id+'/todos.json',
                wait: true
            });
        this.input.val('');
    },
    bindNewTodoEvent:function(){
        var self = this;
        this.$el.find('.btn-new-todo').bind('click', function(){
            self.$el.find('.todo-form.new').hide();
            self.$el.find('.todo-form.form-wrap').show();
        });
        this.$el.find('.btn-cancel-todo').bind('click', function(){
            self.$el.find('.todo-form.new').show();
            self.$el.find('.todo-form.form-wrap').hide();
        });
    }
});
$(document).ready(function(){
    $('#myModal').find('.btn-primary').on('click', function(){
        $('#myModal').data('confirm', 1).modal('hide');
    });
});
//
//$(document).ready(function(){
//    $('.btn-new-todo').live('click', function(){
//        var $wrap = $(this).parents('.todo-new-wrap');
//        $wrap.find('.new').hide();
//        $wrap.find('.form-wrap').show();
//    });
//    $('.btn-cancel-todo').live('click', function(){
//        var $wrap = $(this).parents('.todo-new-wrap');
//        $wrap.find('.new').show();
//        $wrap.find('.form-wrap').hide();
//    });
//    $('.todo-checkbox').live('click', function(){
//        var todo_id = $(this).data('todo-id');
//        var done = $(this).is(':checked')?1:0;
//        var $todo = $(this).parents('.todo');
//        var $all_lists = $(this).parents('.todolist');
//        var $complete_lits = $('.todos.todos-completed', $all_lists);
//        var $uncomplete_lits = $('.todos.todos-uncompleted', $all_lists);
//        $.ajax({
//            type:'post',
//            dataType:'json',
//            data:{done:done},
//            url:'/todo/'+todo_id+'/status.json',
//            success:function(json){
//                if(json) {
//                    if(done) {
//                        $todo.fadeOut(function(){
//                            $todo.addClass('completed').appendTo($complete_lits).fadeIn('fast')
//                        });
//                    } else {
//                        $todo.fadeOut(function(){
//                            $todo.removeClass('completed').prependTo($uncomplete_lits).fadeIn('fast');
//                        })
//                    }
//                }
//            }
//        });
//    });
//
//
//});