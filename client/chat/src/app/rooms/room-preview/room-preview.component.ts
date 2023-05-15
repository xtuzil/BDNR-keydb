import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { Room } from 'src/app/app.service';

@Component({
  selector: 'app-room-preview',
  templateUrl: './room-preview.component.html',
  styleUrls: ['./room-preview.component.scss'],
})
export class RoomPreviewComponent implements OnInit {
  @Input()
  room!: Room;

  @Input()
  selected: boolean = false;

  @Output() selectedEvent = new EventEmitter<Room>();

  constructor() {}

  ngOnInit(): void {
    console.log('ROOM PREVIEW: ', this.room);
  }

  onSelect(event: any) {
    this.selected = !this.selected;
    this.selectedEvent.emit(this.room);
  }
}
