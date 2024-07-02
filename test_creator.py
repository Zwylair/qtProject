import os
import dearpygui.dearpygui as dpg
# import DearPyGui_DragAndDrop as dpg_dnd
# import drag_and_drop_setup
import screeninfo
from test_creator_modules import testmode, drag_testmode, classes
from test_creator_modules.messageboxes import spawn_warning, spawn_info
from cyrillic_support import CyrillicSupport, FontPreset, decode_string

monitor = screeninfo.get_monitors()[0]
monitor_size = (monitor.width, monitor.height)
viewport_size = (833, 700)

dpg.create_context()
# dpg_dnd.initialize()
dpg.create_viewport(
    title='Mionly: test creator', large_icon='icon.ico',
    width=viewport_size[0], height=viewport_size[1],
    x_pos=int(monitor_size[0] / 2 - viewport_size[0] / 2),
    y_pos=int(monitor_size[1] / 2 - viewport_size[1] / 2)
)

fonts = [
    # FontPreset(path='web/fonts/nunito/Nunito-Regular.ttf', size=28, id='nunito_titles', bind_font_as_default=False),
    FontPreset(path='web/fonts/nunito/Nunito-Regular.ttf', size=24, id='nunito', bind_font_as_default=True),
]
with dpg.font_registry():
    for font in fonts:
        CyrillicSupport(font)

with dpg.value_registry():
    dpg.add_string_value(tag='test_creator_test_name', default_value='my test')

#


def save():
    test_name = dpg.get_value('test_creator_test_name')
    test_name_decoded = decode_string(test_name)

    if test_name in os.listdir('tests'):
        spawn_warning('Test with the same name already exists!')
        return

    os.makedirs(f'tests/{test_name_decoded}', exist_ok=True)

    rounds_by_type = {}

    for test_round in test_object.rounds:
        round_type = modules_classes[test_round.__class__]

        if rounds_by_type.get(round_type) is None:
            rounds_by_type[round_type] = []
        rounds_by_type[round_type].append(test_round)

    for test_round_type, rounds in rounds_by_type.items():
        os.makedirs(f'tests/{test_name_decoded}/{test_round_type}', exist_ok=True)

        for index, test_round in enumerate(rounds):
            with open(f'tests/{test_name_decoded}/{test_round_type}/{index}.json', 'w') as file:
                file.write(test_round.dump())

    spawn_info(f'{test_name} was saved!')


with dpg.window(no_title_bar=True, no_resize=True, no_close=True, no_move=True) as window:
    modules = {
        'testmode': testmode.setup,
        # 'drag_testmode':  drag_testmode.setup,
    }
    modules_classes = {
        testmode.TestModeRound: 'testmode',
        # drag_testmode.DragTestModeRound: 'drag_testmode',
    }

    with dpg.group(horizontal=True):
        dpg.add_text('Name of your test: ')
        anchor = dpg.add_input_text(source='test_creator_test_name', width=150)
        save_button = dpg.add_button(label='Save', callback=save)

    test_object = classes.Test([], window, {}, [])

    for initialiser in modules.values():
        initialiser(test_object)

    dpg.add_separator()
    test_object.restricted_parent_children_to_remove = dpg.get_item_children(window)[1]

dpg.set_primary_window(window, True)
# drag_and_drop_setup.setup()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
