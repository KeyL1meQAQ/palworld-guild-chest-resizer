#!/usr/bin/env python3
"""Unit tests for the guild chest logic.

Pure functions over save-shaped dictionaries, so these need no save file, no network
and no libooz — they run anywhere and give the same result every time.

    python -m unittest test_guild_chest -v
"""

import struct
import unittest

import guild_chest as gc


def slot_bytes(index, count, item_id):
    """Build a slot RawData payload the way Palworld serialises one."""
    encoded = item_id.encode("utf-8") + b"\x00" if item_id else b""
    payload = struct.pack("<iii", index, count, len(encoded)) + encoded
    return list(payload.ljust(69, b"\x00"))


def make_container(container_id, guild_id, slotnum, slots):
    """slots: list of (index, count, item_id)."""
    return {
        "key": {"ID": {"value": container_id}},
        "value": {
            "SlotNum": {"value": slotnum, "type": "IntProperty"},
            "Slots": {
                "value": {
                    "values": [
                        {"RawData": {"value": {"values": slot_bytes(i, c, n)}}}
                        for i, c, n in slots
                    ]
                }
            },
            "BelongInfo": {"value": {"GroupId": {"value": guild_id}}},
        },
    }


def guid_to_bytes(guid):
    """Inverse of gc.guid_from_bytes, so fixtures can be written as readable GUIDs."""
    h = guid.replace("-", "")
    words = [int(h[i : i + 8], 16) for i in range(0, 32, 8)]
    return list(struct.pack("<IIII", *words))


def make_world(guilds):
    """guilds: list of (guild_id, container_id, slotnum, slots). None container = no chest."""
    extra, containers = [], []
    for guild_id, container_id, slotnum, slots in guilds:
        extra.append(
            {
                "key": guild_id,
                "value": {
                    "GuildItemStorage": {
                        "value": {"RawData": {"value": {"values": guid_to_bytes(container_id)}}}
                    }
                },
            }
        )
        if slotnum is not None:
            containers.append(make_container(container_id, guild_id, slotnum, slots))
    return {
        "GuildExtraSaveDataMap": {"value": extra},
        "ItemContainerSaveData": {"value": containers},
    }


G1 = "c4f85b2a-4a61-c738-8162-6d9b8e98759a"
G2 = "11111111-2222-3333-4444-555555555555"
G3 = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
C1 = "51551d22-4f25-8d2b-1b19-91a5fe44f6cf"
C2 = "99999999-8888-7777-6666-555555555555"
C3 = "12345678-90ab-cdef-1234-567890abcdef"


class TestGuidDecoding(unittest.TestCase):
    def test_known_vector_from_a_real_save(self):
        raw = [0x22, 0x1D, 0x55, 0x51, 0x2B, 0x8D, 0x25, 0x4F,
               0xA5, 0x91, 0x19, 0x1B, 0xCF, 0xF6, 0x44, 0xFE]
        self.assertEqual(gc.guid_from_bytes(raw), C1)

    def test_round_trips_with_the_fixture_encoder(self):
        for guid in (G1, G2, C1, C3):
            self.assertEqual(gc.guid_from_bytes(guid_to_bytes(guid)), guid)


class TestSlotDecoding(unittest.TestCase):
    def test_index_count_and_item_id(self):
        self.assertEqual(gc.decode_slot(slot_bytes(7, 9999, "Wood")), (7, 9999, "Wood"))

    def test_empty_slot_has_no_item_id(self):
        index, count, name = gc.decode_slot(slot_bytes(3, 0, ""))
        self.assertEqual((index, count), (3, 0))
        self.assertEqual(name, "")


class TestMultipleGuilds(unittest.TestCase):
    def world(self):
        return make_world([
            (G1, C1, 54, [(0, 9999, "Wood"), (5, 100, "Stone")]),
            (G2, C2, 54, [(0, 12, "Cloth")]),
            (G3, C3, 120, [(30, 7, "Coal")]),
        ])

    def test_resizes_every_guild_by_default(self):
        wsd = self.world()
        changed = gc.apply_slot_count(wsd, 358)
        self.assertEqual(len(changed), 3)
        for container in gc.containers_by_id(wsd).values():
            self.assertEqual(container["SlotNum"]["value"], 358)

    def test_reports_previous_value_per_container(self):
        changed = dict((cid, (old, new)) for cid, old, new in
                       gc.apply_slot_count(self.world(), 358))
        self.assertEqual(changed[C1], (54, 358))
        self.assertEqual(changed[C3], (120, 358))

    def test_container_filter_touches_only_that_guild(self):
        wsd = self.world()
        changed = gc.apply_slot_count(wsd, 500, container_filter=C2)
        self.assertEqual(changed, [(C2, 54, 500)])
        containers = gc.containers_by_id(wsd)
        self.assertEqual(containers[C2]["SlotNum"]["value"], 500)
        self.assertEqual(containers[C1]["SlotNum"]["value"], 54)
        self.assertEqual(containers[C3]["SlotNum"]["value"], 120)

    def test_survey_covers_all_guilds(self):
        data = gc.survey(self.world())
        self.assertEqual(set(data), {C1, C2, C3})
        self.assertEqual(data[C1]["max_index"], 5)
        self.assertEqual(data[C1]["occupied"], 2)
        self.assertEqual(data[C3]["guild"], G3)


class TestUnsafeShrink(unittest.TestCase):
    def world(self):
        return make_world([
            (G1, C1, 358, [(0, 9999, "Wood"), (92, 5, "Coal")]),
            (G2, C2, 358, [(0, 12, "Cloth")]),
            (G3, C3, 358, [(200, 1, "Polymer")]),
        ])

    def test_refuses_and_lists_every_offender(self):
        with self.assertRaises(gc.UnsafeShrink) as ctx:
            gc.apply_slot_count(self.world(), 50)
        offenders = {o["container_id"] for o in ctx.exception.offenders}
        # C2's only item is at index 0, so it is not an offender at 50 slots.
        self.assertEqual(offenders, {C1, C3})
        text = str(ctx.exception)
        self.assertIn(G1, text)
        self.assertIn(G3, text)
        self.assertIn("200", text)

    def test_writes_nothing_when_refusing(self):
        wsd = self.world()
        with self.assertRaises(gc.UnsafeShrink):
            gc.apply_slot_count(wsd, 50)
        for container in gc.containers_by_id(wsd).values():
            self.assertEqual(container["SlotNum"]["value"], 358)

    def test_boundary_equal_to_highest_index_is_refused(self):
        wsd = make_world([(G1, C1, 358, [(92, 5, "Coal")])])
        with self.assertRaises(gc.UnsafeShrink):
            gc.apply_slot_count(wsd, 92)

    def test_one_above_highest_index_is_allowed(self):
        wsd = make_world([(G1, C1, 358, [(92, 5, "Coal")])])
        self.assertEqual(gc.apply_slot_count(wsd, 93), [(C1, 358, 93)])

    def test_growing_is_never_blocked(self):
        wsd = self.world()
        self.assertEqual(len(gc.apply_slot_count(wsd, 2466)), 3)


class TestMissingContainers(unittest.TestCase):
    def test_guild_without_a_built_chest_is_skipped(self):
        wsd = make_world([
            (G1, C1, 54, [(0, 1, "Wood")]),
            (G2, C2, None, []),
        ])
        self.assertEqual(gc.apply_slot_count(wsd, 358), [(C1, 54, 358)])

    def test_save_with_no_guilds_at_all(self):
        wsd = {"GuildExtraSaveDataMap": {"value": []}, "ItemContainerSaveData": {"value": []}}
        self.assertEqual(gc.apply_slot_count(wsd, 358), [])
        self.assertEqual(gc.survey(wsd), {})

    def test_save_predating_guilds_has_no_map(self):
        wsd = {"ItemContainerSaveData": {"value": []}}
        self.assertEqual(gc.guild_storage_container_ids(wsd), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
