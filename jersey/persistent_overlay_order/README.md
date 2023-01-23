# Adding persistent overlay order

## Notes

- Currently all users with edit permissoins can edit the overlay order
- There is no need to add an sort order to already existing maps, the code will add it after they are rearranged once
- Currently only works on overlays (see TODOs)

## Step 1
### Adjusting Models

In `models.py` of your core Arches folder add the following line to `MapLayer` class below `searchonly`
```
layersortorder = models.IntegerField(blank=True, null=True, default=None)
```

And under `Node` class below `exportable`
```
layersortorder = models.IntegerField(blank=True, null=True, default=None)
```


## Step 2
### Migrate the model change

One the model has been altered run the following commands in your `venv` to apply model changes

```
(env) python manage.py makemigrations
(env) python manage.py migrate
```


## Step 3
### Add a new view

After migrations, add `reorder_maps.py` to core Arches views folder


## Step 4
### New URL

Add the following url path to the bottom of `urlpatterns` in `urls.py` in your core Arches folder
```
url(r"^reorder_maps", ReorderMaps.as_view(), name ="reorder_maps"),
```


## Step 5
### Map changes

In `map.js` found in `media > js > viewmodels` in your core Arches folder add the following handler
```
        ko.bindingHandlers.sortable.afterMove = function(e) {
            const map_order = ko.observableArray(e.sourceParent())
            var new_order = []
           
            for (let i = 0; i < map_order().length; i++) {
                const element = map_order()[i];
                new_order.push({
                    "maplayerid": element.maplayerid,
                    "layersortorder": i,
                    "is_resource_layer": element.is_resource_layer,
                })
            }
            
            $.ajax({
                type: "POST",
                data: JSON.stringify({
                    map_order: new_order
                }),
                url: arches.urls.root + "reorder_maps",
            })
        }
```

and a sorting function below `var mapLayers` found on line `135`
```
mapLayers = mapLayers.sort((a, b) => parseInt(a.layersortorder) - parseInt(b.layersortorder))
```


## Step 6
### Javascript changes

In the  `javascript.htm` file found in core arches `templates` folder add the following to the bottom of `mapLayers` definition
```
'layersortorder': {{map_layer.layersortorder|default_if_none:"null"|unlocalize}}
```

And under `resource_map_layers` add the following 

```
'layersortorder': {{resource_map_layer.layersortorder|default_if_none:"null"|unlocalize}}
```

# TODOs
- Need to figure out why overlays are not getting `layerorder` in the front end 


- Pull the view out of core arches
- Pull the url out of core arches urls
- Change the ajax call to update rather than post
- Make it work on overlays
- Make it feel like it isn't bodged 
- ~~Wrap the view in try/catch~~
- ~~Worked on dev without js template changes - needs looking into~~
- ~~Worked on dev without sorting function - needs looking into~~
- Fix resource layer order - works on local dev, does not work on live
