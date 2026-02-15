#!/usr/bin/env python3

import dataclasses
import itertools
import math as m
from collections.abc import Callable
from copy import copy
from dataclasses import dataclass
from build123d import (
    Align,
    Axis,
    Box,
    Circle,
    Color,
    Compound,
    CounterSinkHole,
    Cylinder,
    Line,
    Plane,
    Pos,
    Rectangle,
    RectangleRounded,
    Sketch,
    Vector,
    extrude,
    chamfer,
    fillet,
    loft,
    make_face,
)

from .utils import Object, DatumSet, plane_at


@dataclass
class LcdParams:
    module_width: float
    module_height: float
    module_thickness: float
    module_side_clearance: float
    module_front_clearance: float
    module_back_clearance: float
    module_support_thickness: float
    module_support_gap_size: float
    cover_thickness: float
    cover_support_size: float
    cover_back_clearance: float
    cover_side_clearance: float
    bezel_size: float

    @property
    def module_pocket_width(self) -> float:
        return self.module_width + self.module_side_clearance*2

    @property
    def module_pocket_height(self) -> float:
        return self.module_height + self.module_side_clearance*2

    @property
    def module_pocket_depth(self) -> float:
        return (self.module_thickness +
                self.module_front_clearance +
                self.module_back_clearance)

    @property
    def cover_pocket_width(self) -> float:
        return (self.module_pocket_width +
                self.cover_support_size*2 +
                self.cover_side_clearance*2)

    @property
    def cover_pocket_height(self) -> float:
        return (self.module_pocket_height +
                self.cover_support_size +
                self.cover_side_clearance)

    @property
    def cover_pocket_depth(self) -> float:
        return self.cover_thickness + self.cover_back_clearance

    @property
    def cover_width(self) -> float:
        return self.cover_pocket_width - self.cover_side_clearance*2

    @property
    def cover_height(self) -> float:
        return self.cover_pocket_height - self.cover_side_clearance*2

@dataclass
class HoleParams:
    d: float
    x: float
    y: float

@dataclass
class ButtonPosParams:
    x: float
    y: float

@dataclass
class PcbParams:
    width: float
    height: float
    thickness: float

    clearance_top: float
    clearance_bottom: float
    clearance_front: float

    edge_clearance_front: float

    lo_jack_dx: float
    hp_jack_dx: float
    usbc_conn_dx: float
    card_conn_dx: float

    vol_button_dx: float
    vol_up_button_dy: float
    vol_dn_button_dy: float
    power_button_dx: float
    power_button_dy: float
    hold_sw_pos1_dx: float
    hold_sw_pos2_dx: float

    buttons: dict[str, ButtonPosParams]
    holes: dict[str, HoleParams]

    @property
    def hold_sw_center_dx(self) -> float:
        return (self.hold_sw_pos1_dx + self.hold_sw_pos2_dx) / 2

@dataclass
class DpadButtonParams:
    width: float
    height: float
    center_to_origin_dist: float
    center_to_top_dist: float
    edge_to_diagonal_dist: float

@dataclass
class ContactDomeParams:
    height: float
    tip_height: float
    tip_diameter: float
    rim_diameter: float
    travel: float

@dataclass
class Params:
    lcd: LcdParams
    pcb: PcbParams

    outer_depth: float

    wall_thickness_top: float
    wall_thickness_bottom: float
    wall_thickness_front: float
    wall_thickness_back: float
    wall_thickness_side: float

    h3_support_diameter: float
    volume_support_diameter: float
    h5_support_diameter: float
    dpad_support_diameter: float

    debug_header_dx: float
    debug_header_width: float
    debug_header_height: float
    debug_header_clearance_side: float

    jack_diameter: float
    jack_diameter_clearance: float

    usbc_width: float
    usbc_height: float
    usbc_flat_side_length: float
    usbc_clearance: float

    card_width: float
    card_height: float
    card_corner_radius: float
    card_clearance: float
    card_slot_dz: float

    support_screw_diameter: float
    support_screw_head_diameter: float
    support_heat_insert_diameter: float
    support_screw_depth: float

    face_button_diameter: dict[str, float]
    dpad_button: DpadButtonParams

    contact_dome: ContactDomeParams
    face_button_lip_size: float
    face_button_lip_height: float
    face_button_case_clearance: float
    face_button_dome_tip_clearance: float

    startsel_button_smd_height: float
    startsel_button_outer_height: float

    side_pcb_button_body_width: float
    side_pcb_button_body_height: float
    side_pcb_button_body_depth: float
    side_pcb_button_presser_width: float
    side_pcb_button_presser_height: float
    side_pcb_button_presser_depth: float

    side_button_width: float
    side_button_height: float
    side_button_corner_radius: float
    side_button_clearance: float
    side_button_inner_clearance: float
    side_button_lip_pocket_depth: float

    side_button_presser_width: float
    side_button_presser_height: float
    side_button_presser_length: float
    side_button_lip_size: float
    side_button_lip_chamfer_size: float
    side_button_lip_extra_length: float
    side_button_outer_extra_length: float

    side_button_support_dz: float
    side_button_support_pcb_clearance: float
    side_button_support_width: float
    side_button_support_depth: float

    battery_dx: float
    battery_dy: float
    battery_dz: float
    battery_width: float
    battery_height: float
    battery_thickness: float

    bconn_dx: float
    bconn_dy: float
    bconn_width: float
    bconn_height: float
    bconn_depth: float

    batt_spring_dist: float
    batt_spring_tolerance: float

    battbox_thickness: float
    battbox_depth: float
    battbox_clearance_xz: float
    battbox_clearance_y: float
    bconn_clearance: float

    battframe_thickness: float
    battframe_wall_height: float
    battframe_support_diameter: float
    battframe_support_hole_diameter: float
    battframe_support_above_hole_diameter: float
    battframe_support_z_clearance: float
    battframe_connector_y_clearance: float

    lshell_wall_clearance: float
    lshell_shadowline_depth: float
    lshell_cornersquare_thickness: float
    lshell_cornersquare_diameter: float
    lshell_cornersquare_y_extend: float
    lshell_debugheader_side_clearance: float
    lshell_debugheader_top_clearance: float

    @property
    def pcb_attachment_offset_dx(self) -> float:
        return (self.inner_width - self.pcb.width)/2

    @property
    def inner_width(self) -> float:
        return self.outer_width - self.wall_thickness_side*2

    @property
    def inner_height(self) -> float:
        return (self.pcb.height +
                self.pcb.clearance_top +
                self.pcb.clearance_bottom)

    @property
    def inner_origin_dx(self) -> float:
        return self.wall_thickness_side

    @property
    def inner_origin_dy(self) -> float:
        return self.wall_thickness_bottom

    @property
    def outer_width(self) -> float:
        return self.lcd.cover_pocket_width + self.lcd.bezel_size*2

    @property
    def outer_height(self) -> float:
        return (self.inner_height +
                self.wall_thickness_bottom +
                self.wall_thickness_top)

    @property
    def jack_slot_radius(self) -> float:
        return self.jack_diameter/2 + self.jack_diameter_clearance

    @property
    def jack_slot_dz(self) -> float:
        return self.jack_diameter/2

    @property
    def usbc_corner_radius(self) -> float:
        return (self.usbc_height - self.usbc_flat_side_length) / 2

    @property
    def usbc_slot_width(self) -> float:
        return self.usbc_width + self.usbc_clearance*2

    @property
    def usbc_slot_height(self) -> float:
        return self.usbc_height + self.usbc_clearance*2

    @property
    def usbc_slot_corner_radius(self) -> float:
        return self.usbc_corner_radius + self.usbc_clearance

    @property
    def usbc_slot_dz(self) -> float:
        return self.usbc_height/2

    @property
    def card_slot_width(self) -> float:
        return self.card_width + self.card_clearance*2

    @property
    def card_slot_height(self) -> float:
        return self.card_height + self.card_clearance*2

    @property
    def card_slot_corner_radius(self) -> float:
        return self.card_corner_radius + self.card_clearance

    @property
    def side_button_lip_width(self) -> float:
        return self.side_button_width + 2*(self.side_button_lip_size + self.side_button_clearance)

    @property
    def side_button_lip_height(self) -> float:
        return self.side_button_height + 2*(self.side_button_lip_size + self.side_button_clearance)


def get_params() -> Params:
    abxy_button_diameter = 7
    startsel_button_diameter = 4

    dpad_center_x = 27.5
    dpad_center_y = 25.5
    dpad_button_to_center_dist = 10

    return Params(
        lcd = LcdParams(
            module_width = 50.9,
            module_height = 45.8,
            module_thickness = 2.4,
            module_side_clearance = 0.5,
            module_front_clearance = 0.4,
            module_back_clearance = 0.2,
            module_support_thickness = 1.4,
            module_support_gap_size = 5.0,
            cover_thickness = 1.0,
            cover_support_size = 3.5,
            cover_back_clearance = 0.1,
            cover_side_clearance = 0.2,
            bezel_size = 1.5,
        ),
        pcb = PcbParams(
            width = 55,
            height = 95,
            thickness = 1.6,
            clearance_top = 0.8,
            clearance_bottom = 0.2,
            clearance_front = 3,
            edge_clearance_front = 0.6,
            lo_jack_dx = 5,
            hp_jack_dx = 15,
            usbc_conn_dx = 27.5,
            card_conn_dx = 46.9,
            vol_button_dx = 51.15,
            vol_up_button_dy = 77.5,
            vol_dn_button_dy = 62.5,
            power_button_dx = 7.5,
            power_button_dy = 91.15,
            hold_sw_pos1_dx = 16.7,
            hold_sw_pos2_dx = 18.3,
            buttons = {
                "a":          ButtonPosParams(x=49.0, y=35.0),
                "b":          ButtonPosParams(x=40.0, y=41.0),
                "x":          ButtonPosParams(x= 6.0, y=35.0),
                "y":          ButtonPosParams(x=15.0, y=41.0),
                "start":      ButtonPosParams(x=42.8, y= 5.5),
                "select":     ButtonPosParams(x=12.2, y= 5.5),
                "dpad_up":    ButtonPosParams(x=dpad_center_x,
                                              y=dpad_center_y + dpad_button_to_center_dist),
                "dpad_down":  ButtonPosParams(x=dpad_center_x,
                                              y=dpad_center_y - dpad_button_to_center_dist),
                "dpad_left":  ButtonPosParams(x=dpad_center_x - dpad_button_to_center_dist,
                                              y=dpad_center_y),
                "dpad_right": ButtonPosParams(x=dpad_center_x + dpad_button_to_center_dist,
                                              y=dpad_center_y),
            },
            holes = {
                "dpad":   HoleParams(d=4.0, x=dpad_center_x, y=dpad_center_y),
                "volume": HoleParams(d=4.0, x=51.0, y=70.00),
                "h3":     HoleParams(d=2.2, x= 4.0, y=86.00),
                "h5":     HoleParams(d=2.2, x=35.0, y= 2.00),
                "h6":     HoleParams(d=2.2, x=13.0, y=31.75)
            },
        ),
        wall_thickness_top = 2,
        wall_thickness_bottom = 2,
        wall_thickness_front = 2,
        wall_thickness_back = 2,
        wall_thickness_side = 2.4,
        outer_depth = 21.1,
        h3_support_diameter = 7,
        volume_support_diameter = 8,
        h5_support_diameter = 4.8,
        dpad_support_diameter = 6,
        debug_header_dx = 0.73,
        debug_header_height = 2.5,
        debug_header_width = 15.24,
        debug_header_clearance_side = 0.5,
        jack_diameter = 5,
        jack_diameter_clearance = 0.5,
        usbc_width = 8.94,
        usbc_height = 3.26,
        usbc_flat_side_length = 0.7,
        usbc_clearance = 0.5,
        card_width = 12,
        card_height = 1.8,
        card_corner_radius = 0.5,
        card_clearance = 0.5,
        card_slot_dz = 1.8,
        support_screw_diameter = 2,
        support_screw_head_diameter = 3.8,
        support_heat_insert_diameter = 3,
        support_screw_depth = 3,
        face_button_diameter = {
            "a": abxy_button_diameter,
            "b": abxy_button_diameter,
            "x": abxy_button_diameter,
            "y": abxy_button_diameter,
            "start": startsel_button_diameter,
            "select": startsel_button_diameter,
        },
        dpad_button = DpadButtonParams(
            width = 9,
            height = 8.5,
            center_to_origin_dist = dpad_button_to_center_dist,
            center_to_top_dist = 3.5,
            edge_to_diagonal_dist = 2,
        ),
        contact_dome = ContactDomeParams(
            height = 5,
            tip_height = 2.2,
            tip_diameter = 3,
            rim_diameter = 5,
            travel = 2,
        ),
        face_button_lip_size = 1,
        face_button_lip_height = 1.4,
        face_button_case_clearance = 0.25,
        face_button_dome_tip_clearance = 0.1,
        startsel_button_smd_height = 2.4, # includes case clearance
        startsel_button_outer_height = 1.5,
        side_pcb_button_body_width = 4.7,
        side_pcb_button_body_height = 2.3,
        side_pcb_button_body_depth = 1.9,
        side_pcb_button_presser_width = 1.8,
        side_pcb_button_presser_height = 1.2,
        side_pcb_button_presser_depth = 0.8,
        side_button_width = 10,
        side_button_height = 2.5,
        side_button_corner_radius = 1,
        side_button_clearance = 0.3,
        side_button_inner_clearance = 0.5,
        # Lip pocket depth minus extra length needs
        # to be >= PCB button face to PCB edge distance
        side_button_lip_pocket_depth = 1,
        side_button_presser_width = 4,
        side_button_presser_height = 1.5,
        # Presser length needs to be >= A+B where
        #   A = PCB button face to PCB edge distance
        #   B = PCB button travel distance
        side_button_presser_length = 1,
        side_button_lip_size = 0.5,
        side_button_lip_chamfer_size = 0.5,
        # Extra length added to lip to increase part thickness
        side_button_lip_extra_length = 0.2,
        # Must be >= PCB button travel distance
        side_button_outer_extra_length = 1.0,
        side_button_support_dz = 0.3,
        side_button_support_pcb_clearance = 0.3,
        side_button_support_width = 15,
        side_button_support_depth = 6,

        battery_dx = 17.2,
        battery_dy = 28.7,
        battery_dz = 2.8,
        battery_width = 34.3,
        battery_height = 53.5,
        battery_thickness = 5.8,
        bconn_dx = 39.5,
        bconn_dy = 24.4,
        bconn_width = 9,
        bconn_height = 3.5,
        bconn_depth = 6.8,
        batt_spring_dist = 0.8,
        batt_spring_tolerance = 0.2,
        battbox_thickness = 2,
        battbox_depth = 2,
        battbox_clearance_xz = 0.4,
        battbox_clearance_y = 0.1,
        bconn_clearance = 0.8,
        battframe_thickness = 1,
        battframe_wall_height = 3.5,
        battframe_support_diameter = 3.8,
        battframe_support_hole_diameter = 2.2,
        battframe_support_above_hole_diameter = 10,
        battframe_support_z_clearance = 0.2,
        battframe_connector_y_clearance = 2,
        lshell_wall_clearance = 0.3,
        lshell_shadowline_depth = 1.0,
        lshell_cornersquare_diameter = 6,
        lshell_cornersquare_y_extend = 3,
        lshell_cornersquare_thickness = 2.5,
        lshell_debugheader_top_clearance = 0.3,
        lshell_debugheader_side_clearance = 0.3,
    )

def get_pcb_datums(params: Params) -> DatumSet:
    ds = DatumSet()

    ds.add_box("board",
               dimensions = (params.pcb.width,
                             params.pcb.height,
                             params.pcb.thickness),
               alignment = (-1, -1, -1))

    ds.add_point("back_origin",
                 origin = ds.box_point("board", align = (-1, -1, -1)))

    ds.add_point("front_origin",
                 origin = ds.box_point("board", align = (-1, -1, 1)))

    for h_name, h_params in params.pcb.holes.items():
        ds.add_point(f"hole_{h_name}_pos",
                     origin = ds.front_origin,
                     dX = h_params.x,
                     dY = h_params.y)

    ds.add_plane("debug_header_right",
                 plane = ds.board_right,
                 dX = -(params.debug_header_dx -
                        params.debug_header_clearance_side))

    ds.add_plane("debug_header_left",
                 plane = ds.debug_header_right,
                 dX = -(params.debug_header_width +
                        params.debug_header_clearance_side*2))

    for b_name, b_params in params.pcb.buttons.items():
        ds.add_point(f"button_{b_name}_pos",
                     origin = ds.front_origin,
                     dX = b_params.x,
                     dY = b_params.y)

    ds.add_point("button_vol_up_pos",
                 origin = ds.back_origin,
                 dX = params.pcb.vol_button_dx,
                 dY = params.pcb.vol_up_button_dy)

    side_button_zoffset = -(params.side_button_lip_height/2 +
                            params.side_button_inner_clearance +
                            params.side_button_support_dz)

    ds.add_point("button_vol_up_press_pos",
                 origin = ds.button_vol_up_pos,
                 dX = (params.side_pcb_button_body_height +
                       params.side_pcb_button_presser_height),
                 dZ = side_button_zoffset)

    ds.add_point("button_vol_up_support_pos",
                 origin = ds.button_vol_up_pos,
                 dX = (params.side_pcb_button_body_height +
                       params.side_pcb_button_presser_height),
                 dZ = -params.side_button_support_dz)

    ds.add_point("button_vol_dn_pos",
                 origin = ds.back_origin,
                 dX = params.pcb.vol_button_dx,
                 dY = params.pcb.vol_dn_button_dy)

    ds.add_point("button_vol_dn_press_pos",
                 origin = ds.button_vol_dn_pos,
                 dX = (params.side_pcb_button_body_height +
                       params.side_pcb_button_presser_height),
                 dZ = side_button_zoffset)

    ds.add_point("button_vol_dn_support_pos",
                 origin = ds.button_vol_dn_pos,
                 dX = (params.side_pcb_button_body_height +
                       params.side_pcb_button_presser_height),
                 dZ = -params.side_button_support_dz)

    ds.add_point("button_power_pos",
                 origin = ds.back_origin,
                 dX = params.pcb.power_button_dx,
                 dY = params.pcb.power_button_dy)

    ds.add_point("button_power_press_pos",
                 origin = ds.button_power_pos,
                 dY = (params.side_pcb_button_body_height +
                       params.side_pcb_button_presser_height),
                 dZ = side_button_zoffset)

    ds.add_point("button_power_support_pos",
                 origin = ds.button_power_pos,
                 dY = (params.side_pcb_button_body_height +
                       params.side_pcb_button_presser_height),
                 dZ = -params.side_button_support_dz)

    # NOTE: while not part of the PCB there's no better place for this
    ds.add_point("battery_origin",
                 origin = ds.back_origin,
                 dX = params.battery_dx,
                 dY = params.battery_dy,
                 dZ = -params.battery_dz)

    ds.add_box("battery",
               origin = ds.battery_origin,
               dimensions = (params.battery_width,
                             params.battery_height,
                             params.battery_thickness),
               alignment = (-1, -1, 1))

    ds.add_point("bconn_origin",
                 origin = ds.back_origin,
                 dX = params.bconn_dx,
                 dY = params.bconn_dy)

    ds.add_box("bconn",
               origin = ds.bconn_origin,
               dimensions = (params.bconn_width,
                             params.bconn_height,
                             params.bconn_depth),
               alignment = (-1, -1, 1))

    return ds

def get_upper_shell_datums(params: Params,
                           pcb_ds: DatumSet) -> DatumSet:
    ds = DatumSet()

    ds.add_box("outer_wall",
               dimensions = (params.outer_width,
                             params.outer_height,
                             params.outer_depth - params.wall_thickness_back),
               alignment = (-1, -1, -1))

    ds.add_point("outer_origin",
                 origin = ds.box_point("outer_wall", align = (-1, -1, -1)))

    ds.add_point("lcd_cover_pocket_origin",
                 origin = ds.box_point("outer_wall", align = (0, 1, 1)),
                 dY = -params.lcd.bezel_size)

    ds.add_box("lcd_cover_pocket",
               origin = ds.lcd_cover_pocket_origin,
               dimensions = (params.lcd.cover_pocket_width,
                             params.lcd.cover_pocket_height,
                             params.lcd.cover_pocket_depth),
               alignment = (0, 1, 1))

    ds.add_point("lcd_module_pocket_origin",
                 origin = ds.lcd_cover_pocket_origin,
                 dY = -(params.lcd.cover_support_size + params.lcd.cover_side_clearance),
                 dZ = -params.lcd.cover_pocket_depth)

    ds.add_box("lcd_module_pocket",
               origin = ds.lcd_module_pocket_origin,
               dimensions = (params.lcd.module_pocket_width,
                             params.lcd.module_pocket_height,
                             params.lcd.module_pocket_depth),
               alignment = (0, 1, 1))

    ds.add_point("lcd_support_gap_pocket_origin",
                 origin = ds.box_point("lcd_module_pocket", align = (0, -1, -1)))

    ds.add_box("lcd_support_gap_pocket",
               origin = ds.lcd_support_gap_pocket_origin,
               dimensions = (params.lcd.module_pocket_width,
                             params.lcd.module_support_gap_size,
                             params.lcd.module_support_thickness),
               alignment = (0, -1, 1))

    ds.add_plane("lcd_support_back",
                 plane = ds.lcd_support_gap_pocket_back,
                 X = ds.outer_origin.X,
                 Y = ds.outer_origin.Y)

    ds.add_point("inner_origin",
                 origin = ds.outer_origin,
                 dX = params.inner_origin_dx,
                 dY = params.inner_origin_dy)

    ds.add_box("inner_wall",
               origin = ds.inner_origin,
               dimensions = (params.inner_width,
                             params.inner_height,
                             ds.lcd_support_back.origin.Z - ds.inner_origin.Z),
               alignment = (-1, -1, -1))

    ds.add_point("pcb_attachment",
                 origin = ds.inner_origin,
                 dX = params.pcb_attachment_offset_dx,
                 dY = params.pcb.clearance_bottom,
                 Z = ds.lcd_support_back.origin.Z - params.pcb.clearance_front)

    ds.add_reference("pcb", pcb_ds,
                     Pos(ds.pcb_attachment - pcb_ds.front_origin))

    rs = [
        "hole_h3_pos",
        "hole_h5_pos",
        "hole_volume_pos",
        "hole_dpad_pos",
        "button_a_pos",
        "button_b_pos",
        "button_x_pos",
        "button_y_pos",
        "button_start_pos",
        "button_select_pos",
        "button_dpad_up_pos",
        "button_dpad_down_pos",
        "button_dpad_left_pos",
        "button_dpad_right_pos",
        "debug_header_left",
        "debug_header_right",
        "back_origin",
        "front_origin",
        "battery_origin",
        "battery_front",
        "battery_back",
        "battery_left",
        "battery_right",
        "battery_top",
        "battery_bottom",
        "bconn_origin",
        "bconn_back",
        "bconn_left",
        "bconn_right",
    ]

    for r in rs:
        ds.add_alias(f"pcb_{r}", r, "pcb")

    ds.add_plane("bottom_slot_plane",
                 plane = ds.outer_wall_bottom,
                 X = ds.pcb_back_origin.X,
                 Z = ds.pcb_back_origin.Z)

    ds.add_plane("lower_inner_wall_front",
                 plane = ds.outer_wall_front,
                 dZ = -params.wall_thickness_front)

    return ds

def get_lower_shell_datums(params: Params,
                           ushell_ds: DatumSet) -> DatumSet:
    ds = DatumSet()

    ds.add_box("plate",
               dimensions = (ushell_ds.box_dimension("outer_wall", "x"),
                             ushell_ds.box_dimension("outer_wall", "y"),
                             params.wall_thickness_back),
               alignment = (-1, -1, -1))

    ds.add_point("ushell_attachment",
                 origin = ds.box_point("plate", align = (-1, -1, 1)))

    ds.add_reference("ushell", ushell_ds,
                     Pos(ds.ushell_attachment - ushell_ds.outer_origin))

    return ds

def get_battery_frame_datums(params: Params,
                             ushell_ds: DatumSet) -> DatumSet:
    ds = DatumSet()

    ds.add_point("ushell_attachment",
                 dX = params.battbox_thickness,
                 dY = params.battbox_thickness,
                 dZ = params.battframe_wall_height)

    pt = ushell_ds.pcb.box_point("battery", align = (-1, -1, 1))
    ds.add_reference("ushell", ushell_ds,
                     Pos(ds.ushell_attachment - pt))

    ds.add_alias("volume_pos", "pcb_hole_volume_pos", "ushell")
    ds.add_alias("dpad_pos", "pcb_hole_dpad_pos", "ushell")

    return ds


def make_dpad_arrow_face(width: float,
                         height: float,
                         center_to_origin_dist: float,
                         center_to_top_dist: float,
                         edge_to_diagonal_dist: float,
                         edge_offset: float|None = None):
    hsqrt2 = m.sqrt(2) / 2

    if edge_offset:
        width += edge_offset*2
        height += edge_offset*2
        center_to_origin_dist += edge_offset
        center_to_top_dist += edge_offset
        edge_to_diagonal_dist -= edge_offset * hsqrt2 / (1 + 2*hsqrt2)

    top_y = center_to_top_dist
    top_x = width / 2
    mid_y = top_x - center_to_origin_dist + (2 * edge_to_diagonal_dist * hsqrt2)
    bot_y = top_y - height
    bot_x = top_x - (mid_y - bot_y)

    verts = [
        (+top_x, top_y),
        (+top_x, mid_y),
        (+bot_x, bot_y),
        (-bot_x, bot_y),
        (-top_x, mid_y),
        (-top_x, top_y),
        (+top_x, top_y), # extra for wraparound
    ]

    return make_face([Line(v, vn) for v, vn in zip(verts, verts[1:])])

def make_side_button_face(width: float,
                          height: float,
                          corner_radius: float,
                          edge_offset: float|None = None):
    if edge_offset:
        width += edge_offset*2
        height += edge_offset*2
        corner_radius += edge_offset

    return RectangleRounded(width, height, corner_radius)

def make_side_button_inner_face(width: float,
                                height: float,
                                chamfer_size: float,
                                edge_offset: float|None = None):
    if edge_offset:
        width += edge_offset*2
        height += edge_offset*2
        chamfer_size += edge_offset

    face = Rectangle(width, height)
    return chamfer(face.vertices(), chamfer_size)



def make_upper_shell(params: Params, datums: DatumSet) -> Compound:
    # Flag for LCD cover / no cover
    has_lcd_cover = True

    # Flag to use heat inserts vs. tapped holes for screws
    has_heat_inserts = True

    # Shell outer surface
    shell = (
        Pos(datums.outer_origin) *
        Box(
            datums.box_dimension("outer_wall", "x"),
            datums.box_dimension("outer_wall", "y"),
            datums.box_dimension("outer_wall", "z"),
            align = Align.MIN,
        )
    )

    # LCD cover pocket
    lcd_cover_pocket = (
        datums.lcd_cover_pocket_back *
        Box(
            datums.box_dimension("lcd_cover_pocket", "x"),
            datums.box_dimension("lcd_cover_pocket", "y"),
            datums.box_dimension("lcd_cover_pocket", "z"),
            align = (Align.CENTER, Align.MAX, Align.MIN),
        )
    )

    # LCD module pocket
    lcd_module_pocket_depth = datums.box_dimension("lcd_module_pocket", "z")
    if not has_lcd_cover:
        lcd_module_pocket_depth += datums.box_dimension("lcd_cover_pocket", "z")

    lcd_module_pocket = (
        datums.lcd_module_pocket_back *
        Box(
            datums.box_dimension("lcd_module_pocket", "x"),
            datums.box_dimension("lcd_module_pocket", "y"),
            lcd_module_pocket_depth,
            align = (Align.CENTER, Align.MAX, Align.MIN),
        )
    )

    # Gap to slide the LCD module through during assembly
    lcd_support_gap_pocket = (
        Pos(datums.lcd_support_gap_pocket_origin) *
        Box(
            datums.box_dimension("lcd_support_gap_pocket", "x"),
            datums.box_dimension("lcd_support_gap_pocket", "y"),
            datums.box_dimension("lcd_support_gap_pocket", "z"),
            align = (Align.CENTER, Align.MIN, Align.MAX)
        )
    )

    # Main section of inner pocket, up to the LCD support
    main_inner_pocket = (
        Pos(datums.inner_origin) *
        Box(
            datums.box_dimension("inner_wall", "x"),
            datums.box_dimension("inner_wall", "y"),
            datums.box_dimension("inner_wall", "z"),
            align = Align.MIN,
        )
    )

    # Supports on the upper half of the PCB
    upper_pcb_supports = []
    upper_hole_data = [
        ("h3",     datums.inner_wall_left,  Align.MIN),
        ("volume", datums.inner_wall_right, Align.MAX),
    ]

    for h_name, wall, xalign in upper_hole_data:
        h_origin = datums.point(f"pcb_hole_{h_name}_pos")
        s_diam = getattr(params, f"{h_name}_support_diameter")

        xs = abs(wall.origin.X - h_origin.X) + s_diam/2
        ys = s_diam
        zs = datums.lcd_support_back.origin.Z - h_origin.Z

        h_origin.X = wall.origin.X

        upper_pcb_supports.append(
            Pos(h_origin) *
            Box(
                xs, ys, zs,
                align = (xalign, Align.CENTER, Align.MIN)
            )
        )

    # Slot for debug header
    debug_header_slot = (
        plane_at(datums.inner_wall_top,
                 x = datums.pcb_debug_header_right.origin.X) *
        Box(
            datums.pcb_debug_header_right.origin.X - datums.pcb_debug_header_left.origin.X,
            datums.lcd_support_back.origin.Z - datums.outer_wall_back.origin.Z,
            params.wall_thickness_top,
            align = (Align.MAX, Align.MIN, Align.MAX)
        )
    )

    # Audio jack slots
    jack_slot = (
        datums.bottom_slot_plane *
        Pos(Y = -params.jack_slot_dz) *
        Cylinder(
            params.jack_slot_radius,
            params.wall_thickness_bottom,
            align = (Align.CENTER, Align.CENTER, Align.MAX),
        )
    )

    hp_jack_slot = Pos(X = params.pcb.hp_jack_dx) * copy(jack_slot)
    lo_jack_slot = Pos(X = params.pcb.lo_jack_dx) * copy(jack_slot)

    # USB-C port slot
    usbc_slot = (
        datums.bottom_slot_plane *
        Pos(X = params.pcb.usbc_conn_dx,
            Y = -params.usbc_slot_dz) *
        extrude(RectangleRounded(width = params.usbc_slot_width,
                                 height = params.usbc_slot_height,
                                 radius = params.usbc_slot_corner_radius),
                amount = -params.wall_thickness_bottom)
    )

    # Memory card slot
    card_slot = (
        datums.bottom_slot_plane *
        Pos(X = params.pcb.card_conn_dx,
            Y = -params.card_slot_dz) *
        extrude(RectangleRounded(width = params.card_slot_width,
                                 height = params.card_slot_height,
                                 radius = params.card_slot_corner_radius),
                amount = -params.wall_thickness_bottom)
    )

    # Make the front wall a reasonable thickness
    lower_inner_pocket_maxdepth = (datums.outer_wall_front.origin.Z -
                                   datums.lcd_support_back.origin.Z)
    assert lower_inner_pocket_maxdepth > params.wall_thickness_front

    lower_inner_pocket_pcb_edge_offset_x = params.pcb_attachment_offset_dx + params.pcb.edge_clearance_front
    lower_inner_pocket_pcb_edge_offset_y = params.pcb.clearance_bottom + params.pcb.edge_clearance_front

    lower_inner_pocket_width = params.inner_width
    lower_inner_pocket_width -= lower_inner_pocket_pcb_edge_offset_x*2

    lower_inner_pocket_height = datums.lcd_support_gap_pocket_bottom.origin.Y - datums.inner_origin.Y
    lower_inner_pocket_height -= lower_inner_pocket_pcb_edge_offset_y

    lower_inner_pocket_depth = lower_inner_pocket_maxdepth - params.wall_thickness_front

    lower_inner_pocket = (
        plane_at(datums.lcd_support_back,
                 projected_origin = datums.inner_origin) *
        Pos(X = lower_inner_pocket_pcb_edge_offset_x,
            Y = lower_inner_pocket_pcb_edge_offset_y) *
        Box(lower_inner_pocket_width,
            lower_inner_pocket_height,
            lower_inner_pocket_depth,
            align = Align.MIN)
    )

    # Extend the edge supports up to the PCB front face
    lower_pcb_edge_support = (
        plane_at(datums.lcd_support_back,
                 projected_origin = datums.inner_origin) *
        Box(
            params.inner_width,
            datums.lcd_support_gap_pocket_bottom.origin.Y - datums.inner_origin.Y,
            datums.lcd_support_back.origin.Z - datums.pcb_front_origin.Z,
            align = (Align.MIN, Align.MIN, Align.MAX)
        )
    )

    lower_pcb_edge_support -= (Pos(Z = -lower_inner_pocket_depth) *
                               copy(lower_inner_pocket))

    # Add supports in lower region
    lower_pcb_supports = []
    lower_hole_data = [
        ("dpad", Cylinder, None,                     None),
        ("h5",   Box,      datums.inner_wall_bottom, Align.MIN),
    ]

    for h_name, shape_class, wall, yalign in lower_hole_data:
        h_origin = datums.point(f"pcb_hole_{h_name}_pos")
        s_diam = getattr(params, f"{h_name}_support_diameter")
        zs = datums.lower_inner_wall_front.origin.Z - datums.pcb_hole_dpad_pos.Z

        if shape_class is Cylinder:
            lower_pcb_supports.append(
                plane_at(datums.lower_inner_wall_front,
                         projected_origin = h_origin) *
                Cylinder(
                    radius = s_diam/2,
                    height = zs,
                    align = (Align.CENTER, Align.CENTER, Align.MAX),
                )
            )
        else:
            assert yalign is not None

            xs = s_diam
            ys = h_origin.Y - wall.origin.Y + s_diam/2

            h_origin.Y = wall.origin.Y

            lower_pcb_supports.append(
                plane_at(datums.lower_inner_wall_front,
                         projected_origin = h_origin) *
                Box(
                    xs, ys, zs,
                    align = (Align.CENTER, yalign, Align.MAX),
                )
            )

    # Add holes to supports for screws / heat inserts
    if has_heat_inserts:
        support_hole_diameter = params.support_heat_insert_diameter
    else:
        support_hole_diameter = params.support_screw_diameter

    support_hole_depth = params.support_screw_depth

    support_holes = []
    support_hole_positions = [
        datums.pcb_hole_h3_pos,
        datums.pcb_hole_h5_pos,
        datums.pcb_hole_dpad_pos,
        datums.pcb_hole_volume_pos,
    ]

    for h_origin in support_hole_positions:
        support_holes.append(
            Pos(h_origin) *
            Cylinder(
                radius = support_hole_diameter/2,
                height = support_hole_depth,
                align = (Align.CENTER, Align.CENTER, Align.MIN)
            )
        )

    # Cut holes for face buttons
    face_button_holes = []

    for b_name in params.pcb.buttons:
        diam = params.face_button_diameter.get(b_name)
        if diam is None:
            continue

        face_button_holes.append(
            plane_at(datums.outer_wall_front,
                     projected_origin = datums.point(f"pcb_button_{b_name}_pos")) *
            Cylinder(
                radius = diam/2,
                height = params.wall_thickness_front,
                align = (Align.CENTER, Align.CENTER, Align.MAX)
            )
        )

    # Cut holes for d-pad buttons
    dpad_button_face = make_dpad_arrow_face(**dataclasses.asdict(params.dpad_button))
    dpad_button_data = [
        ("dpad_up",     0),
        ("dpad_left",   90),
        ("dpad_down",   180),
        ("dpad_right",  270),
    ]

    for b_name, rotation in dpad_button_data:
        face_button_holes.append(
            plane_at(datums.outer_wall_front,
                     projected_origin = datums.point(f"pcb_button_{b_name}_pos")) *
            extrude(
                dpad_button_face.rotate(Axis.Z, rotation),
                amount = -params.wall_thickness_front,
            )
        )

    # Cut holes for side buttons (volume and power)
    side_button_face = make_side_button_face(params.side_button_width,
                                             params.side_button_height,
                                             params.side_button_corner_radius,
                                             params.side_button_clearance)
    side_button_face = side_button_face.rotate(Axis.X, -90)
    side_button_hole = extrude(side_button_face, amount = 10)

    # Pocket for lip to allow clearance for assembly
    side_button_lip_face = Rectangle(params.side_button_lip_width + params.side_button_inner_clearance*2,
                                     params.side_button_lip_height + params.side_button_inner_clearance*4/3)
    side_button_lip_face = Pos(Y = -params.side_button_inner_clearance/3) * side_button_lip_face
    side_button_lip_face = side_button_lip_face.rotate(Axis.X, -90)

    wall_dist_vol = abs(datums.pcb.button_vol_up_press_pos.X - datums.inner_wall_right.origin.X)
    pcb_dist_vol  = abs(datums.pcb.button_vol_up_press_pos.X - datums.pcb.board_right.origin.X)
    wall_dist_pwr = abs(datums.pcb.button_power_press_pos.Y - datums.inner_wall_top.origin.Y)
    pcb_dist_pwr  = abs(datums.pcb.button_power_press_pos.Y - datums.pcb.board_top.origin.Y)
    side_button_data = [
        ("vol_up", -90, wall_dist_vol, pcb_dist_vol),
        ("vol_dn", -90, wall_dist_vol, pcb_dist_vol),
        ("power",    0, wall_dist_pwr, pcb_dist_pwr),
    ]

    side_button_holes = []
    side_button_supports = []
    for b_name, rotation, wall_dist, pcb_dist in side_button_data:
        pos = Pos(datums.pcb.get_point(f"button_{b_name}_press_pos"))
        hole = side_button_hole + extrude(side_button_lip_face,
                                          amount=wall_dist + params.side_button_lip_pocket_depth)
        hole = pos * hole.rotate(Axis.Z, rotation)
        side_button_holes.append(hole)

        support_size = wall_dist - pcb_dist - params.side_button_support_pcb_clearance
        pos = Pos(datums.pcb.get_point(f"button_{b_name}_support_pos"))
        if rotation == 0:
            loc = Pos(Y = wall_dist) * pos
            support = Box(params.side_button_support_width,
                          support_size,
                          params.side_button_support_depth,
                          align = (Align.CENTER, Align.MAX, Align.MIN))
        else:
            loc = Pos(X = wall_dist) * pos
            support = Box(support_size,
                          params.side_button_support_width,
                          params.side_button_support_depth,
                          align = (Align.MAX, Align.CENTER, Align.MIN))

        support = loc * support

        side_button_supports.append(support)

    # Cut screw holes for mounting back plate
    corner_hole = CounterSinkHole(
        params.support_screw_diameter/2,
        params.support_screw_head_diameter/2,
        params.wall_thickness_side,
    )

    corner_holes = []
    for corner_x, corner_y in ((0, 0), (0, 1), (1, 0), (1, 1)):
        adj_y = params.lshell_wall_clearance + params.lshell_cornersquare_diameter/2

        pos = datums.inner_origin
        pos += Vector(X = -params.wall_thickness_side,
                      Y = adj_y)
        pos += Vector(X = (params.inner_width + params.wall_thickness_side*2) * corner_x,
                      Y = (params.inner_height - adj_y*2) * corner_y,
                      Z = params.lshell_cornersquare_diameter/2)

        hole = corner_hole.rotate(Axis.Y, corner_x*180 - 90)

        corner_holes.append(Pos(pos) * hole)

    # CSG to generate case
    if has_lcd_cover:
        shell -= lcd_cover_pocket

    shell -= itertools.chain(
        face_button_holes,
        side_button_holes,
        corner_holes,
        [
            lcd_module_pocket,
            lcd_support_gap_pocket,
            main_inner_pocket,
            debug_header_slot,
            hp_jack_slot,
            lo_jack_slot,
            usbc_slot,
            card_slot,
            lower_inner_pocket,
        ],
    )

    shell += itertools.chain(
        upper_pcb_supports,
        lower_pcb_supports,
        side_button_supports,
        [
            lower_pcb_edge_support,
        ]
    )

    shell -= support_holes

    return shell


def make_lower_shell(params: Params, datums: DatumSet) -> Compound:
    shell = Box(
        datums.box_dimension("plate", "x"),
        datums.box_dimension("plate", "y"),
        datums.box_dimension("plate", "z"),
        align = Align.MIN,
    )

    # Shadow line to minimize visibility of seam with front shell
    pos = datums.ushell.inner_origin.project_to_plane(datums.plate_front)
    shell += (
        Pos(X = pos.X + params.lshell_wall_clearance,
            Y = pos.Y + params.lshell_wall_clearance,
            Z = datums.box_dimension("plate", "z")) *
        Box(
            datums.ushell.box_dimension("inner_wall", "x") - params.lshell_wall_clearance*2,
            datums.ushell.box_dimension("inner_wall", "y") - params.lshell_wall_clearance*2,
            params.lshell_shadowline_depth,
            align = Align.MIN,
        )
    )

    # Plate for covering debug header
    pos = datums.ushell.pcb.debug_header_left.origin.project_to_plane(datums.plate_front)
    shell += (
        Pos(X = pos.X, Z = pos.Z) *
        Pos(X = params.lshell_debugheader_side_clearance,
            Y = datums.ushell.box_dimension("outer_wall", "y")) *
        Box(
            (params.debug_header_width +
             params.debug_header_clearance_side*2 -
             params.lshell_debugheader_side_clearance*2),
            (params.wall_thickness_top +
             params.lshell_wall_clearance),
            (datums.ushell.pcb_front_origin.Z -
             datums.plate_front.origin.Z -
             params.lshell_debugheader_top_clearance),
            align = (Align.MIN, Align.MAX, Align.MIN)
        )
    )

    # Battery box
    battbox = (
        Pos(datums.ushell.pcb_battery_origin.project_to_plane(datums.plate_front)) *
        Pos(X = -params.battbox_thickness,
            Y = -params.battbox_thickness) *
        Box(
            datums.ushell.box_dimension("pcb_battery", "x") + params.battbox_thickness*2,
            datums.ushell.box_dimension("pcb_battery", "y") + params.battbox_thickness*2,
            params.battbox_depth,
            align = Align.MIN,
        )
    )

    # Space for the battery
    battbox_hole = (
        Pos(datums.ushell.pcb_battery_origin.project_to_plane(datums.ushell.pcb_battery_back)) *
        Pos(X = -params.battbox_clearance_xz,
            Y = -params.battbox_clearance_y,
            Z = -params.battbox_clearance_xz) *
        Box(
            datums.ushell.box_dimension("pcb_battery", "x") + params.battbox_clearance_xz*2,
            datums.ushell.box_dimension("pcb_battery", "y") + params.battbox_clearance_y,
            datums.ushell.box_dimension("pcb_battery", "z") + params.battbox_clearance_xz*2,
            align = Align.MIN,
        )
    )

    shell -= battbox_hole
    battbox -= battbox_hole

    # Battery connector
    bconn_to_batt_dist_y = (datums.ushell.pcb.battery_bottom.origin.Y -
                            datums.ushell.pcb.bconn_top.origin.Y)

    # Specified spring compression is 0.8mm +/- 0.2mm
    assert abs(bconn_to_batt_dist_y - params.batt_spring_dist) <= params.batt_spring_tolerance

    battbox -= (
        Pos(datums.ushell.pcb_bconn_origin.project_to_plane(datums.ushell.pcb_bconn_back)) *
        Pos(X = -params.bconn_clearance,
            Y = -params.bconn_clearance,
            Z = -params.bconn_clearance) *
        Box(
            datums.ushell.pcb.box_dimension("bconn", "x") + params.bconn_clearance*2,
            datums.ushell.pcb.box_dimension("bconn", "y") + params.bconn_clearance + bconn_to_batt_dist_y - params.battbox_clearance_y,
            datums.ushell.pcb.box_dimension("bconn", "z") + params.bconn_clearance*2,
            align = Align.MIN,
        )
    )

    # Add squares on the corners to hold mounting screws
    squares = []
    for corner_x, corner_y in ((0, 0), (0, 1), (1, 0), (1, 1)):
        square = Box(params.lshell_cornersquare_thickness,
                     params.lshell_cornersquare_diameter + params.lshell_cornersquare_y_extend,
                     params.lshell_cornersquare_diameter,
                     align = Align.MIN)
        square -= (
            Pos(X = corner_x * params.lshell_cornersquare_thickness,
                Y = params.lshell_cornersquare_diameter/2,
                Z = params.lshell_cornersquare_diameter/2) * (
                    Cylinder(params.support_heat_insert_diameter/2,
                             params.lshell_cornersquare_thickness,
                             align = (Align.CENTER, Align.CENTER,
                                      Align.MIN if corner_x == 0 else Align.MAX))
                    .rotate(Axis.Y, 90)
                )
        )

        adj_x = params.lshell_cornersquare_thickness + params.lshell_wall_clearance*2
        adj_y = params.lshell_wall_clearance*2

        pos = datums.ushell.inner_origin.project_to_plane(datums.plate_front)
        pos += Vector(X = (params.inner_width - adj_x) * corner_x,
                      Y = (params.inner_height - adj_y) * corner_y)
        pos += Vector(X = params.lshell_wall_clearance,
                      Y = params.lshell_wall_clearance)

        msquare = square
        if corner_y > 0:
            msquare = square.mirror(Plane.XZ)

        squares.append(Pos(pos) * msquare)

    shell += itertools.chain(
        squares,
        battbox,
    )

    return shell

def make_battery_frame(params: Params, datums: DatumSet) -> Compound:
    thickness = params.battframe_thickness + params.battframe_wall_height

    # Main body supporting the battery
    frame = Box(
        datums.ushell.box_dimension("pcb_battery", "x") + params.battbox_thickness*2,
        datums.ushell.box_dimension("pcb_battery", "y") + params.battbox_thickness*2,
        thickness,
        align = Align.MIN,
    )

    frame -= (
        Pos(X = params.battbox_thickness,
            Y = params.battbox_thickness) *
        Box(
            datums.ushell.box_dimension("pcb_battery", "x") + params.battbox_clearance_xz,
            datums.ushell.box_dimension("pcb_battery", "y") + params.battbox_clearance_y,
            params.battframe_wall_height,
            align = Align.MIN,
        )
    )

    # Avoid volume up/down buttons
    for pos in (datums.ushell.pcb.button_vol_up_pos, datums.ushell.pcb.button_vol_dn_pos):
        frame -= (
            Pos(X = pos.X - params.bconn_clearance,
                Y = pos.Y) *
            Box(
                params.side_pcb_button_body_height + params.bconn_clearance*2,
                params.side_pcb_button_body_width + params.bconn_clearance*2,
                thickness,
                align = (Align.MIN, Align.CENTER, Align.MIN)
            )
        )

    # Support columns
    support_length = datums.ushell.pcb_front_origin.Z - params.battframe_support_z_clearance
    table = (
        (datums.dpad_pos,   0),
        (datums.volume_pos, params.battframe_wall_height),
    )

    for pos, zoffset in table:
        loc = Pos(X = pos.X, Y = pos.Y, Z = zoffset)
        frame += loc * (
            Pos(Y = params.battframe_support_diameter/4) *
            Box(
                params.battframe_support_diameter,
                params.battframe_support_diameter/2,
                thickness - zoffset,
                align = (Align.CENTER, Align.CENTER, Align.MIN),
            ) +
            Cylinder(
                params.battframe_support_diameter/2,
                support_length - zoffset,
                align = (Align.CENTER, Align.CENTER, Align.MIN),
            )
        )

        # add this to volume support for pressing the PCB down
        if zoffset != 0:
            frame += loc * Cylinder(
                params.battframe_support_diameter/2 + 0.6,
                support_length - zoffset - 1.4,
                align = (Align.CENTER, Align.CENTER, Align.MIN),
            )

            frame -= loc * Pos(Z = -zoffset) * Box(
                params.battframe_support_above_hole_diameter,
                params.battframe_support_above_hole_diameter,
                zoffset,
                align = (Align.CENTER, Align.CENTER, Align.MIN),
            )

            # HACK provide clearance between head of screw and battery
            s_head_thickness = 0.6

            frame -= loc * Cylinder(
                radius = 6,
                height = s_head_thickness,
                align = (Align.CENTER, Align.CENTER, Align.MIN),
            )

            # reinforce very thin piece created by above hack
            for dy in (-1.85, 1.85):
                frame += loc * Pos(Y = dy, Z = s_head_thickness) * Box(
                    5, 5, 1.8,
                    align = (Align.CENTER, Align.CENTER, Align.MIN),
                )

            # main reinforcement
            frame += loc * Pos(X = -0.65, Z = s_head_thickness) * Box(
                5, 18, 1.8,
                align = (Align.MAX, Align.CENTER, Align.MIN),
            )

        frame -= loc * Cylinder(
            params.battframe_support_hole_diameter/2,
            support_length,
            align = (Align.CENTER, Align.CENTER, Align.MIN),
        )

    # Battery connector
    bconn_to_batt_dist_y = (datums.ushell.pcb.battery_bottom.origin.Y -
                            datums.ushell.pcb.bconn_top.origin.Y)

    frame -= (
        Pos(datums.ushell.pcb_bconn_origin.project_to_plane(datums.ushell.pcb_bconn_back)) *
        Pos(X = -params.bconn_clearance,
            Y = -params.bconn_clearance,
            Z = -params.bconn_clearance) *
        Box(
            datums.ushell.pcb.box_dimension("bconn", "x") + params.bconn_clearance*2,
            (datums.ushell.pcb.box_dimension("bconn", "y") +
             params.bconn_clearance + bconn_to_batt_dist_y +
             params.battframe_connector_y_clearance),
            datums.ushell.pcb.box_dimension("bconn", "z") + params.bconn_clearance*2,
            align = Align.MIN,
        )
    )

    return frame


def mkface_dpad(params: DpadButtonParams,
                clearance: float):
    def fn(offset: float):
        return make_dpad_arrow_face(edge_offset = offset - clearance,
                                    **dataclasses.asdict(params))

    return fn

def mkface_circle(diameter: float,
                  clearance: float):
    def fn(offset: float):
        return Circle(radius=(diameter + offset)/2 - clearance)

    return fn

def make_dome_button(
    mkface: Callable[[float], Sketch],
    dome_height: float,
    dome_tip_height: float,
    dome_tip_hole_diameter: float,
    dome_rim_diameter: float,
    travel: float,
    enclosed_height: float,
    enclosure_thickness: float,
    lip_size: float,
    lip_height: float,
    edge_fillet_radius: float = 0,
) -> Compound:
    # Origin for part
    oz = -dome_tip_height

    # Compute available height inside the enclosure
    inside_height = enclosed_height - dome_height + dome_tip_height

    # Divide height between the lip and the lofted section
    loft_height = inside_height - lip_height

    # Button which extends out of the enclosure
    btn_face   = Pos(Z = oz + inside_height) * mkface(0)
    btn_height = enclosure_thickness + travel
    btn_part   = extrude(btn_face, amount = btn_height)

    # Round off sharp-edged profiles to reduce ballooning at the corners
    elist = list(btn_part.edges().filter_by(Axis.Z))
    if edge_fillet_radius > 0 and len(elist) > 1:
        btn_part = fillet(elist, edge_fillet_radius)

    # Lip inside the enclosure, matching the button profile
    lip_face = Pos(Z = oz + loft_height) * mkface(lip_size)
    lip_part = extrude(lip_face, amount = lip_height)

    # Press face which contacts the dome; lofted to the lip profile
    press_face = Pos(Z = oz) * Circle(radius = dome_rim_diameter/2)
    press_part = loft([press_face, lip_face])

    # Hole for the dome tip
    tip_hole = Cylinder(
        radius = dome_tip_hole_diameter/2,
        height = dome_tip_height,
        align = (Align.CENTER, Align.CENTER, Align.MAX)
    )

    # Assemble part
    return btn_part + lip_part + press_part - tip_hole

def make_startselect_button(
    mkface: Callable[[float], Sketch],
    smd_button_height: float,
    button_height: float,
    enclosed_height: float,
    enclosure_thickness: float,
    lip_size: float,
) -> Compound:
    # Part origin
    oz = smd_button_height

    # Compute available height inside the enclosure
    inside_height = enclosed_height - smd_button_height

    # Button which extends out of the enclosure
    btn_face   = Pos(Z = oz + inside_height) * mkface(0)
    btn_height = enclosure_thickness + button_height
    btn_part   = extrude(btn_face, amount = btn_height)

    # Press face with lip matching the button profile
    press_face = Pos(Z = oz) * mkface(lip_size)
    press_part = extrude(press_face, amount = inside_height)

    # Assemble part
    return btn_part + press_part


def make_dome_buttons(params: Params, upper_shell_datums: DatumSet) -> list[Object]:
    objects: list[Object] = []

    dome_tip_hole_diameter = (params.contact_dome.tip_diameter +
                              params.face_button_dome_tip_clearance*2)
    face_button_enclosed_height = (
        upper_shell_datums.lower_inner_wall_front.origin.Z -
        upper_shell_datums.pcb_front_origin.Z
    )

    dome_args = {
        "dome_height": params.contact_dome.height,
        "dome_tip_height": params.contact_dome.tip_height,
        "dome_tip_hole_diameter": dome_tip_hole_diameter,
        "dome_rim_diameter": params.contact_dome.rim_diameter,
        "travel": params.contact_dome.travel,
        "enclosed_height": face_button_enclosed_height,
        "enclosure_thickness": params.wall_thickness_front,
        "lip_size": params.face_button_lip_size,
        "lip_height": params.face_button_lip_height,
    }

    # Create the D-pad arrow buttons
    mkface_dpad_fn = mkface_dpad(params = params.dpad_button,
                                 clearance = params.face_button_case_clearance)
    dpad_button = make_dome_button(mkface_dpad_fn, **dome_args)

    objects.append(Object(
        name = "button-dpad",
        compound = dpad_button,
        renderable = False,
    ))

    # Now handle the ABXY buttons
    circ_dome_button_diameter = copy(params.face_button_diameter)
    del circ_dome_button_diameter["start"]
    del circ_dome_button_diameter["select"]

    mkface_circ_fn = {
        bdiam: mkface_circle(diameter = bdiam,
                             clearance = params.face_button_case_clearance)
        for bdiam in set(circ_dome_button_diameter.values())
    }

    circ_button = {
        bdiam: make_dome_button(mkface = mkface_circ, **dome_args)
        for bdiam, mkface_circ in mkface_circ_fn.items()
    }

    # Start/select buttons use a different design
    startsel_button_diameter = {
        "start":  params.face_button_diameter["start"],
        "select": params.face_button_diameter["select"],
    }

    mkface_startsel_fn = {
        bdiam: mkface_circle(diameter = bdiam,
                             clearance = params.face_button_case_clearance)
        for bdiam in set(startsel_button_diameter.values())
    }

    startsel_args = {
        "smd_button_height": params.startsel_button_smd_height,
        "button_height": params.startsel_button_outer_height,
        "enclosed_height": face_button_enclosed_height,
        "enclosure_thickness": params.wall_thickness_front,
        "lip_size": params.face_button_lip_size,
    }

    startsel_button = {
        bdiam: make_startselect_button(mkface = mkface_startsel, **startsel_args)
        for bdiam, mkface_startsel in mkface_startsel_fn.items()
    }

    for diam, button in itertools.chain(circ_button.items(), startsel_button.items()):
        objects.append(Object(
            name = f"button-dome-circular-{diam}mm",
            compound = button,
            renderable = False,
        ))

    # Generate renderable buttons
    dome_button_data = [
        ("a",          0),
        ("b",          0),
        ("x",          0),
        ("y",          0),
        ("start",      0),
        ("select",     0),
        ("dpad_up",    0),
        ("dpad_left",  90),
        ("dpad_down",  180),
        ("dpad_right", 270),
    ]

    for bname, rot_angle in dome_button_data:
        if bname in "abxy":
            button = circ_button[params.face_button_diameter[bname]]
        elif bname in ["start", "select"]:
            button = startsel_button[params.face_button_diameter[bname]]
        else:
            button = dpad_button

        button = button.rotate(Axis.Z, rot_angle)
        button = button.translate(upper_shell_datums.point(f"pcb_button_{bname}_pos"))

        if bname not in ["start", "select"]:
            button = button.translate(Vector(0, 0, params.contact_dome.height))

        button.name = "button-" + bname.replace("_", "-")
        button.color = Color(0.6, 0.6, 0.6, 1)
        objects.append(Object(
            name = button.name,
            compound = button,
            exportable = False,
        ))

    return objects


def make_side_button(params: Params,
                     wall_dist: float,
                     wall_thickness: float) -> Compound:
    # Part origin is at the button's press_pos

    # Extrude lip which rests on inner surface of case
    lip_face = make_side_button_inner_face(params.side_button_lip_width,
                                           params.side_button_lip_height,
                                           params.side_button_lip_chamfer_size)
    lip_length = wall_dist - params.side_button_presser_length
    lip_length += params.side_button_lip_extra_length
    lip_length += params.side_button_presser_length
    part = (
        extrude(lip_face, lip_length)
        .rotate(Axis.X, -90)
    )

    # Extrude the outer button face which passes through the case wall
    outer_face = make_side_button_face(params.side_button_width,
                                       params.side_button_height,
                                       params.side_button_corner_radius)
    outer_length = wall_thickness - params.side_button_lip_extra_length
    outer_length += params.side_button_outer_extra_length
    part += (
        Pos(Y = lip_length) *
        extrude(outer_face, outer_length)
        .rotate(Axis.X, -90)
    )

    return part


def make_pcb(params: PcbParams,
             datums: DatumSet) -> Compound:
    pcb = Box(
        datums.box_dimension("board", "x"),
        datums.box_dimension("board", "y"),
        datums.box_dimension("board", "z"),
        align = Align.MIN
    )

    holes = []
    for h_params in params.holes.values():
        holes.append(
            Pos(X = h_params.x, Y = h_params.y) *
            Cylinder(
                radius = h_params.d/2,
                height = params.thickness,
                align = (Align.CENTER, Align.CENTER, Align.MIN),
            )
        )

    pcb -= holes
    return pcb


def make_battery(params: Params) -> Compound:
    batt = (
        Pos(X = params.battery_thickness/2) *
        Box(
            params.battery_width - params.battery_thickness,
            params.battery_height,
            params.battery_thickness,
            align = (Align.MIN, Align.MIN, Align.MAX)
        )
    )

    side = Cylinder(params.battery_thickness/2,
                    params.battery_height,
                    align = (Align.MIN, Align.MAX, Align.MAX),
                    rotation = (90, 0, 0))

    batt += side
    batt += Pos(X = params.battery_width - params.battery_thickness) * side

    return batt

def make_battery_connector(params: Params) -> Compound:
    bconn = Box(params.bconn_width,
                params.bconn_height,
                params.bconn_depth,
                align = (Align.MIN, Align.MIN, Align.MAX))

    return bconn

def make_side_pcb_button(params: Params) -> Compound:
    body = Box(params.side_pcb_button_body_width,
               params.side_pcb_button_body_height,
               params.side_pcb_button_body_depth,
               align = (Align.CENTER, Align.MIN, Align.MAX))

    body += (
        Pos(Y = params.side_pcb_button_body_height,
            Z = -params.side_pcb_button_body_depth/2) *
        Box(params.side_pcb_button_presser_width,
            params.side_pcb_button_presser_height,
            params.side_pcb_button_presser_depth,
            align = (Align.CENTER, Align.MIN, Align.CENTER))
    )

    return body

def build() -> list[Object]:
    objects: list[Object] = []
    params = get_params()
    pcb_ds = get_pcb_datums(params)
    ushell_ds = get_upper_shell_datums(params, pcb_ds)
    lshell_ds = get_lower_shell_datums(params, ushell_ds)
    bframe_ds = get_battery_frame_datums(params, ushell_ds)

    upper_shell = make_upper_shell(params, ushell_ds)
    upper_shell.color = Color(0.8, 0.8, 0.8, 1)
    objects.append(Object(
        name = "upper-shell",
        compound = upper_shell,
        datums = ushell_ds,
    ))

    lshell_loc = lshell_ds.get_ref("ushell").loc.inverse()
    lower_shell = lshell_loc * make_lower_shell(params, lshell_ds)
    lower_shell.color = Color(0.7, 0.5, 0.5, 1)
    objects.append(Object(
        name = "lower-shell",
        datums = lshell_ds,
        datums_xform = lshell_loc,
        compound = lower_shell,
    ))

    bframe_loc = bframe_ds.get_ref("ushell").loc.inverse()
    bframe = bframe_loc * make_battery_frame(params, bframe_ds)
    bframe.color = Color(0.5, 0.5, 0.7, 1)
    objects.append(Object(
        name = "battery-frame",
        compound = bframe,
    ))

    objects += make_dome_buttons(params, ushell_ds)

    pcb = Pos(ushell_ds.pcb_back_origin) * make_pcb(params.pcb, pcb_ds)
    pcb.color = Color(0.2, 0.8, 0.2, 1)
    objects.append(Object(
        name = "pcb",
        datums = pcb_ds,
        datums_xform = ushell_ds.get_ref("pcb").loc,
        compound = pcb,
        manufacturable = False,
    ))

    batt = Pos(ushell_ds.pcb_battery_origin) * make_battery(params)
    batt.color = Color(0.15, 0.15, 0.15, 1)
    objects.append(Object(
        name = "battery",
        compound = batt,
        manufacturable = False,
    ))

    bconn = Pos(ushell_ds.pcb_bconn_origin) * make_battery_connector(params)
    bconn.color = Color(0.15, 0.15, 0.4, 1)
    objects.append(Object(
        name = "battery-connector",
        compound = bconn,
        manufacturable = False,
    ))


    side_pcb_button = make_side_pcb_button(params)

    wall_dist_vol = abs(ushell_ds.pcb.button_vol_up_press_pos.X - ushell_ds.inner_wall_right.origin.X)
    wall_dist_pwr = abs(ushell_ds.pcb.button_power_press_pos.Y - ushell_ds.inner_wall_top.origin.Y)

    side_vol_button = make_side_button(params, wall_dist_vol, params.wall_thickness_side)
    side_pwr_button = make_side_button(params, wall_dist_pwr, params.wall_thickness_top)

    table = (
        ("volume-up",   -90, "vol_up", side_vol_button, False, True),
        ("volume-down", -90, "vol_dn", side_vol_button, False, True),
        ("volume",        0, "vol_up", side_vol_button, True,  False),
        ("power",         0, "power",  side_pwr_button, True,  True),
    )

    for name, angle, dname, body, _, rendered in table:
        if not rendered:
            continue

        pcb_pos = ushell_ds.pcb.get_point(f"button_{dname}_pos")
        pcb_btn = Pos(pcb_pos) * side_pcb_button.rotate(Axis.Z, angle)
        pcb_btn.color = Color(0.6, 0.6, 0.6, 1)
        objects.append(Object(
            name = f"pcb-button-{name}",
            compound = pcb_btn,
            manufacturable = False,
        ))

    for name, angle, dname, body, exported, rendered in table:
        press_pos = ushell_ds.pcb.get_point(f"button_{dname}_press_pos")
        btn = Pos(press_pos) * body.rotate(Axis.Z, angle)
        btn.color = Color(0.2, 0.2, 0.2, 1)
        objects.append(Object(
            name = f"button-{name}",
            compound = btn,
            exportable = exported,
            renderable = rendered,
        ))

    return objects
