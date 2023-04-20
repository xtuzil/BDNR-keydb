import { ChangeDetectorRef, Component, Input, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { AppService, Message } from '../app.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent implements OnInit {
  @Input()
  roomCode: string = '';

  chatMessages$!: Observable<Message[]>;
  messageControl = new FormControl('');
  message = '';

  constructor(private service: AppService) {}

  ngOnInit(): void {
    this.chatMessages$ = this.service.chatMessages.asObservable();
  }

  sendMessage() {
    this.message = this.messageControl.value ?? '';
    console.log('SENDING MESSAGE: ', this.message);
    this.service.sendMessage(this.roomCode, this.message);
    this.messageControl.reset();
  }
}
