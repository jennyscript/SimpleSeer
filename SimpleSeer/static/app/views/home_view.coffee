View = require './view'
FrameView = require './frame'
template = require './templates/home'
application = require 'application'

module.exports = class HomeView extends View
  initialize: =>
    super()
    $.datepicker.setDefaults $.datepicker.regional['']
    @addSubview "frameview", FrameView, '#frame-container'
    $(window).on('scroll', @scrollSearchbar)
    Highcharts.setOptions
      global:
        useUTC: false
      title:
        text:null
      yAxis:
        title:
          text: ''
      tooltip:
        snap:100
        crosshairs:true
        #enabled:false
      plotOptions:
        series:
          #stickyTracking: false
          lineWidth:2
      credits:
        enabled:
          false
      legend:
        enabled: false
      chart:
        animation: false



  
  events:
    "click #realtimecontrol": "realtimeControl"
    #"click #controlbarchangebtn": "changeTime"
    "click li.timespan_toggle": "toggleTimespanControl"
    "change #chart-interval": "changeInterval"
    
  id: 'home-view'
  template: template
  getRenderData: =>
    return chartcount : application.charts.length

  postRender: =>
    $('#date-from').datetimepicker {timeFormat: 'hh:mm:ss', onClose: (=> @changeTime())}
    $('#date-to').datetimepicker {timeFormat: 'hh:mm:ss', onClose: (=> @changeTime())}
    $('#chart-interval').selectmenu()
    #$('#chart-interval').attr('value',application.charts.timeframe)
    @_makeNow()
    $('#date-to').attr 'disabled', 'disabled'
    application.framesets.fetch()

  _makeNow: =>
    if !application.charts.paused
      if @_now
        clearInterval @_now
      $('#date-to').datetimepicker('setDate',new Date())
      @_now = setInterval(->
        interval = application.charts.timeframe * 1000
        dt = new Date()
        $('#date-to').datetimepicker('setDate',dt)
        dtt = new Date(Math.round(dt.getTime() - interval))
        $('#date-from').datetimepicker('setDate',dtt)
      , 1000)
    else
      if @_now
        clearInterval @_now      

  changeInterval: (e)=>
    application.charts.timeframe = e.target.value
    @changeTime()

  realtimeControl: (evt)=>
    if evt
      evt.preventDefault()
    @toggleControlBar()
    if application.charts.paused
      application.charts.unpause()
      $('#date-to').attr 'disabled', 'disabled'
    else
      application.charts.pause()
      $('#date-to').removeAttr "disabled"      
    @_makeNow()
    return
        
  changeTime: =>
    if application.charts.paused
      f = $('#date-from')
      t = $('#date-to')
      #dt = moment()
      dt = new Date
      if !f.datetimepicker('getDate')
        f.datetimepicker('setDate', dt)
    
      if !t.datetimepicker('getDate')
        t.datetimepicker('setDate', dt.subtract('minutes',1))
    
      _dtf = $('#date-from').datetimepicker('getDate')
      _dtt = $('#date-to').datetimepicker('getDate')
      if !_dtf
        _dtf = new Date()
        $('#date-from').datetimepicker('setDate',_dtf)
      if !_dtt
        _dtt = new Date()
        $('#date-to').datetimepicker('setDate',_dtt)
      _dtf = _dtf.getTime() / 1000
      _dtt = _dtt.getTime() / 1000
      for obj in application.charts.models
        obj.view.update _dtf,_dtt
    else
      application.charts.timeframe = $('#chart-interval').attr('value')
      tf = Math.round((new Date()).getTime() / 1000) - application.charts.timeframe
      for obj in application.charts.models
        obj.view.update tf
  toggleControlBar: =>
    $('#control-bar-realtime').toggleClass 'hide'
    $('#control-bar-paused').toggleClass 'hide'
    return

  toggleTimespanControl: (evt)->
    evt.preventDefault()
    time_controls = $('#search_bar li.time_controls')
    search_box = $('#search_bar input.search')
    initial_time_width = time_controls.width()
    initial_search_width = search_box.width()
    direction = 1
    if time_controls.is ":hidden"
      direction = -1
    time_controls.animate({width:'toggle'},{
      step: (now, fx) ->
        if direction == 1
          width = initial_search_width+initial_time_width-now
        else
          width = initial_search_width-now
        search_box.width(width)
    })

  # only needed until subnav is supported in bootstrap https://github.com/twitter/bootstrap/issues/1189
  scrollSearchbar: =>
    search_bar = $('#search_bar')
    if $(window).scrollTop() >= 17
      search_bar.addClass 'subnav-fixed'
    else
      search_bar.removeClass 'subnav-fixed'
