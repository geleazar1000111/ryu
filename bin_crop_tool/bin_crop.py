import yaml
#import odin
import odin.model
from odin.utils.bin_localization import BinLocalization
from odin.tools.visualize import SendVisualizer, VisualizationType
from odin.app import App


def load_configs():
    with open("/etc/odin/policies/datacollection/config.yaml") as file:
        configs = yaml.load(file)
    #for key in configs['models']['bin_models']:
        #print(configs['models']['bin_models'])
    #print(configs['models']['bin_models'],['bin_model'])
    return configs


def load_world():
    with open("/etc/odin/world.yaml") as file:
        configs = yaml.load(file)
    return configs


def create_bin_crop_visualizer():
    DC_configs = load_configs()
    viz_binlocalizer = SendVisualizer('Bin Localizer', VisualizationType.IMAGE)
    #print(DC_configs['models']['bin_models']['bin model']['config']['saved_model_dir'])
    bin_model = odin.model.factory(**DC_configs['models']['bin_models']['bin model'])
    #bin_model.initialize()
    app = odin.app.app_factory()
    #app.visualization_manager.register(viz_binlocalizer)
    world = load_world()
    for bin_name, bin_config in DC_configs['bins'].items():
        bin_config = dict(bin_config)  # We don't modify the original config file
        if 'localizer' in bin_config:
            binlocalizer = BinLocalization(
                visualizer=viz_binlocalizer,
                cam=app.hardware_manager[bin_config['overcam_transform_name']],
                crop=bin_config['localizer']['bin_pose_crop'],
                model=bin_model,
                world=world,
                bin_transform_name=bin_config['bin_transform_name'],
                cam_transform_name=bin_config['overcam_transform_name'],
                #np_recorder=bin_localizer_np_recorder,
                #img_recorder=bin_localizer_rgb_recorder,
                #json_recorder=bin_localizer_meta_recorder
            )
            binlocalizer.visualize()


def main():
    create_bin_crop_visualizer()
    #load_configs()

if __name__ == '__main__':
    main()