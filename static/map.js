$(function(){
    var MapLocation = Backbone.Model.extend({
        defaults: function(){
            return {
                lat: 37.7749295,
                lng: -122.41941550000001,
                zoom: 16
            }
        }
    });

    var FoodTruck = Backbone.Model.extend({
        defaults: function(){
            return {
                selected: false,
            }
        }
    });

    var FoodTruckList = Backbone.Collection.extend({
        model: FoodTruck,

        url: '/foodtrucks'
    });

    var FoodTrucks = new FoodTruckList;

    var FoodTruckView = Backbone.View.extend({
        template: _.template('<h1><%=name%></h1><dl><dt>Address</dt><dd><%=address%></dd><dt>Food Types</dt><dd><%=type%></dd></dl>'),

        initialize: function(options) {
            this.map = options['map'];
            var lat = this.model.get('lat'),
                lng = this.model.get('lng'),
                truckposition = new google.maps.LatLng(lat, lng);

            this.marker = new google.maps.Marker({
                position: truckposition,
                icon: { url: '/static/food_truck.png' },
                title: this.model.get('name')
            });
            google.maps.event.addListener(this.marker, 'click', this.displayInfo.bind(this));
            this.listenTo(this.model, "change", this.update);
        },

        render: function() {
            if (this.marker.getMap() != this.map) {
                this.marker.setMap(this.map);
            }
        },

        remove: function() {
            this.marker.setMap(null);
        },

        displayInfo: function() {
            var details = $('#details'),
                ui      = $('#ui');
            ui.removeClass('expand');
            details.empty()
            details.append(this.template(this.model.toJSON()));
            ui.addClass('expand');
            this.setSelected();
        },

        setSelected: function() {
            FoodTrucks.each(function(model){
                model.set({selected: false});
            });
            this.model.set({selected: true});
        },

        update: function() {
            if (this.model.get('selected') == true) {
                this.marker.setIcon('/static/food_truck_selected.png');
            } else {
                this.marker.setIcon('/static/food_truck.png');
            }
        }
    });

    var MapView = Backbone.View.extend({
        el: $('#map-canvas'),

        events: {
            "keypress #search-field": 'handleSearch'
        },

        initialize: function() {
            var position = new google.maps.LatLng(37.7749295, -122.41941550000001),
                mapOptions = {
                    center: position,
                    zoom: 16,
                    mapTypeId: google.maps.MapTypeId.ROADMAP,
                    panControl: false,
                    zoomControl: true,
                    mapTypeControl: true,
                    scaleControl: true,
                    streetViewControl: true,
                    overviewMapControl: false
                };

            // @todo move this to a templating system to make localization easier
            this.search       = $('<div id="ui"><input type="text" id="search-field" placeholder="Enter Location"/><div id="details"/></div>');
            this.geocoder     = new google.maps.Geocoder;
            this.views        = {};
            this.searchfield  = $('#search-field', this.search);
            this.listenTo(this.model, "change", this.render);

            if (navigator.geolocation)
            {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        var lat = position.coords.latitude,
                            lng = position.coords.longitude;
                        mapOptions['center'] = new google.maps.LatLng(lat, lng);
                        this.drawMap(mapOptions);
                    }.bind(this),

                    function() {
                        this.drawMap(mapOptions);
                    }
                );
            }
            else
            {
                this.drawMap(mapOptions);
            }
        },

        drawMap: function(mapOptions) {
            this.map          = new google.maps.Map(this.el, mapOptions);
            this.map.controls[google.maps.ControlPosition.TOP_LEFT].push(this.search[0]);
            this.addMarker(mapOptions.center);

            var idlelistener = google.maps.event.addListener(this.map, 'idle', function() {
                this.drawTrucks();
            }.bind(this));

            var initlistener = google.maps.event.addListener(this.map, 'idle', function() {
                initlistener.remove();
                this.autocomplete = new google.maps.places.Autocomplete(this.searchfield[0], {bounds:this.map.getBounds()});
                this.loadTrucks();
            }.bind(this));
        },

        render: function() {
            var lat      = this.model.get('lat'),
                lng      = this.model.get('lng'),
                zoom     = this.model.get('zoom');
                position = new google.maps.LatLng(lat, lng);

            this.map.setCenter(position);
            this.map.setZoom(zoom);

            this.addMarker(position);
        },

        loadTrucks: function() {
            FoodTrucks.fetch({
                data: {
                    location_box: this.map.getBounds().toUrlValue()
                },
                success: this.drawTrucks.bind(this)
            });
        },

        drawTrucks: function() {
            this.removeOutsideView();
            this.addInView();
        },

        addOne: function(truck) {
            // only add the view if we don't already have one
            if (this.views[truck.get('id')] == undefined) {
                this.views[truck.get('id')] = new FoodTruckView({model: truck, map: this.map});
            }
            this.views[truck.get('id')].render();
        },

        removeOne: function(truck) {
            // only remove the view if we already have it
            if (this.views[truck.get('id')]) {
                this.views[truck.get('id')].remove();
            }
        },

        addInView: function() {
            var bounds  = this.map.getBounds(),
                ne      = bounds.getNorthEast(),
                sw      = bounds.getSouthWest(),
                min_lat = sw.lat()
                min_lng = sw.lng()
                max_lat = ne.lat()
                max_lng = ne.lng();

            trucks = FoodTrucks.filter(function(model) {
                var lat = model.get('lat'),
                    lng = model.get('lng');
                return min_lat <= lat && max_lat >= lat && min_lng <= lng && max_lng >= lng;
            });
            _.each(trucks, this.addOne, this);
        },

        removeOutsideView: function() {
            var bounds  = this.map.getBounds(),
                ne      = bounds.getNorthEast(),
                sw      = bounds.getSouthWest(),
                min_lat = sw.lat()
                min_lng = sw.lng()
                max_lat = ne.lat()
                max_lng = ne.lng();

            trucks = FoodTrucks.filter(function(model) {
                var lat = model.get('lat'),
                    lng = model.get('lng');
                return min_lat > lat || max_lat < lat || min_lng > lng || max_lng < lng;
            });
            _.each(trucks, this.removeOne, this);
        },

        addMarker: function(position) {
            if (this.marker)
            {
                this.marker.setMap(null);
                delete this.marker;
            }

            this.marker = new google.maps.Marker({
                position: position,
                map: this.map
            });
        },


        handleSearch: function(e) {
            if (e.keyCode != 13)
            {
                $('#ui').removeClass('expand');
                return;
            }
            if (!this.searchfield.val()) return;



            var search_query = {
                address: this.searchfield.val(),
                location: new google.maps.LatLng(this.model.get('lat'), this.model.get('lng'))
            };

            this.geocoder.geocode(search_query, this.handleGeocodeResult.bind(this));
            e.target.blur();
        },

        handleGeocodeResult: function (result, status) {
            if (status != google.maps.GeocoderStatus.OK) {
                this.handleGeocodeError(status);
            } else {
                this.model.set({
                    lat: result[0].geometry.location.lat(),
                    lng: result[0].geometry.location.lng()
                });
            }
        },

        handleGeocodeError: function(status){
            // @todo do this better
            alert('Geocode Error!');
        }

    });

    maplocation = new MapLocation;
    map         = new MapView({ model: maplocation });
    map.render();
});