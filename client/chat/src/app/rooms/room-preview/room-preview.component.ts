import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'app-room-preview',
  templateUrl: './room-preview.component.html',
  styleUrls: ['./room-preview.component.scss'],
})
export class RoomPreviewComponent implements OnInit {
  @Input()
  code: string = '';

  @Input()
  name: string = '';

  @Input()
  selected: boolean = false;

  @Input()
  lastMessage: string = '';

  @Output() selectedEvent = new EventEmitter<string>();

  constructor() {}

  ngOnInit(): void {}

  onSelect(event: any) {
    this.selected = !this.selected;
    this.selectedEvent.emit(this.code);
  }
}
